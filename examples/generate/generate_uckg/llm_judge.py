"""
llm_judge.py

Evaluates a fine-tuned model's predictions against reference answers using an
LLM judge (Gemini), scoring each prediction on 5 dimensions (Relevance,
Completeness, Accuracy, Specificity, Clarity) from 0-10.

Expects LLaMA-Factory style predictions JSONL with fields:
    { "prompt": "...", "predict": "...", "label": "..." }

Outputs:
  - <stem>_judged.jsonl : per-example scores + judge reasoning
  - summary table printed to stdout

Usage:
    python3 examples/generate/generate_uckg/llm_judge.py \\
        --predictions examples/generate/generate_uckg/eval_1hop_eval_results.jsonl
"""

import argparse
import asyncio
import json
import os
import re
import statistics
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(".env")

API_KEY = os.getenv("SYNTHESIZER_API_KEY")
BASE_URL = os.getenv("SYNTHESIZER_BASE_URL")
MODEL = os.getenv("SYNTHESIZER_MODEL", "gemini-1.5-flash")

DEFAULT_CONCURRENCY = 8

DIMENSIONS = ["relevance", "completeness", "accuracy", "specificity", "clarity"]

JUDGE_PROMPT = """You are an expert cybersecurity evaluator judging a fine-tuned language model's answer to a domain question.

Score the MODEL ANSWER against the REFERENCE ANSWER on five dimensions, each from 0 (worst) to 10 (best):

1. Relevance — Does the model answer address the question that was asked?
2. Completeness — Does the model answer cover all the key facts present in the reference?
3. Accuracy — Are the factual claims in the model answer correct? A claim is correct if it is supported by the reference or is standard, non-contradictory cybersecurity knowledge. Any statement that contradicts the reference counts as an accuracy failure.
4. Specificity — Does the model answer use concrete identifiers, phase names, protocol names, mechanisms, and values where appropriate, rather than vague generalities?
5. Clarity — Is the model answer well-structured, unambiguous, and readable?

Scoring guidance:
- Different wording from the reference is fine — do NOT penalize paraphrasing. Only penalize missing facts or wrong facts.
- A shorter answer that is correct and covers the key points should score high on Accuracy and Relevance, even if Completeness is lower.
- If the model adds facts not in the reference, those do not raise Completeness; if they contradict the reference, lower Accuracy.
- Be strict but fair. Do not give 10 unless the answer is genuinely excellent on that dimension.

Return ONLY a JSON object in this exact schema, no markdown, no preamble:

{{
  "relevance": <int 0-10>,
  "completeness": <int 0-10>,
  "accuracy": <int 0-10>,
  "specificity": <int 0-10>,
  "clarity": <int 0-10>,
  "reasoning": "<one or two sentences explaining the main driver of the scores>"
}}

---
QUESTION:
{question}

REFERENCE ANSWER:
{reference}

MODEL ANSWER:
{prediction}
---"""


def strip_chat_template(prompt: str) -> str:
    """Remove LLaMA-Factory chat template wrapping to recover the raw question."""
    cleaned = re.sub(r"^\s*(?:system.*?\n)?user\s*\n+", "", prompt, count=1, flags=re.DOTALL)
    cleaned = re.sub(r"assistant\s*\n*\s*$", "", cleaned, count=1, flags=re.DOTALL)
    return cleaned.strip()


def load_predictions(path: str) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            records.append({
                "question": strip_chat_template(row["prompt"]),
                "reference": row["label"],
                "prediction": row["predict"],
            })
    return records


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    m = _JSON_RE.search(text)
    if not m:
        raise ValueError(f"no JSON object found in response: {text[:200]!r}")
    return json.loads(m.group(0))


async def _call(client: AsyncOpenAI, rec: dict, temperature: float) -> dict:
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                question=rec["question"],
                reference=rec["reference"],
                prediction=rec["prediction"],
            ),
        }],
        max_tokens=2000,
        temperature=temperature,
    )
    choice = resp.choices[0]
    content = choice.message.content
    finish = getattr(choice, "finish_reason", None)
    if not content:
        raise RuntimeError(f"empty content (finish_reason={finish})")
    parsed = _extract_json(content)
    for dim in DIMENSIONS:
        if dim not in parsed:
            raise ValueError(f"missing dimension {dim!r} in response: {parsed}")
        parsed[dim] = int(parsed[dim])
        if not 0 <= parsed[dim] <= 10:
            raise ValueError(f"{dim} out of range: {parsed[dim]}")
    return parsed


async def judge_one(client: AsyncOpenAI, sem: asyncio.Semaphore, rec: dict) -> dict:
    async with sem:
        try:
            return await _call(client, rec, temperature=0.1)
        except Exception as e1:
            try:
                return await _call(client, rec, temperature=0.0)
            except Exception as e2:
                raise RuntimeError(f"both attempts failed: {e1} | retry: {e2}") from e2


def summarize(scores: list[dict]) -> dict:
    summary = {}
    for dim in DIMENSIONS:
        vals = [s[dim] for s in scores]
        summary[dim] = {
            "avg": statistics.mean(vals),
            "min": min(vals),
            "max": max(vals),
        }
    overall = statistics.mean([summary[d]["avg"] for d in DIMENSIONS])
    summary["overall_avg"] = overall
    return summary


def print_table(summary: dict, n: int):
    print()
    print("=" * 60)
    print(f"LLM Judge Summary ({n} predictions)")
    print("=" * 60)
    print(f"{'Dimension':<15} {'Avg':>6}  {'Min':>4}  {'Max':>4}")
    print("-" * 60)
    for dim in DIMENSIONS:
        s = summary[dim]
        print(f"{dim.capitalize():<15} {s['avg']:>6.2f}  {s['min']:>4}  {s['max']:>4}")
    print("-" * 60)
    print(f"{'Overall avg':<15} {summary['overall_avg']:>6.2f}")
    print("=" * 60)


def default_output_for(input_path: str) -> str:
    p = Path(input_path)
    return str(p.with_name(f"{p.stem}_judged.jsonl"))


async def run(predictions_file: str, output_file: str, concurrency: int):
    assert API_KEY and BASE_URL, "SYNTHESIZER_API_KEY and SYNTHESIZER_BASE_URL must be set in .env"

    records = load_predictions(predictions_file)
    print(f"Loaded {len(records)} predictions from {predictions_file}")
    print(f"Judge model: {MODEL} | concurrency: {concurrency}")

    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120.0)
    sem = asyncio.Semaphore(concurrency)

    tasks = [judge_one(client, sem, r) for r in records]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    scores = []
    failed = 0
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        for rec, res in zip(records, results):
            if isinstance(res, Exception):
                failed += 1
                print(f"  [fail] {rec['question'][:60]}... -> {res}")
                continue
            scores.append(res)
            out.write(json.dumps({
                "question": rec["question"],
                "reference": rec["reference"],
                "prediction": rec["prediction"],
                **{d: res[d] for d in DIMENSIONS},
                "reasoning": res.get("reasoning", ""),
            }, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(scores)} judged rows to {output_file}")
    if failed:
        print(f"Failed: {failed}")

    if scores:
        summary = summarize(scores)
        print_table(summary, len(scores))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--predictions", required=True, help="Path to LLaMA-Factory predictions JSONL")
    parser.add_argument("--output", default=None, help="Output path (default: <stem>_judged.jsonl)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    out = args.output or default_output_for(args.predictions)
    asyncio.run(run(args.predictions, out, args.concurrency))
