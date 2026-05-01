"""
generate_eval_questions.py

Reads a training Q&A file (ShareGPT format) and, for each pair, asks Gemini
to write ONE new question that targets the same fact with different wording.
The original answer must remain correct. Output is a held-out eval set in the
same ShareGPT format: { new_question, original_answer }.

Usage:
    python3 examples/generate/generate_uckg/generate_eval_questions.py \\
        --input examples/generate/generate_uckg/bluesmacking_property_qa.jsonl

    # Explicit output path:
    python3 examples/generate/generate_uckg/generate_eval_questions.py \\
        --input examples/generate/generate_uckg/bluesmacking_1hop.jsonl \\
        --output examples/generate/generate_uckg/bluesmacking_1hop_eval.jsonl

If --output is omitted, the script writes alongside the input as
<stem>_eval.jsonl.
"""

import argparse
import asyncio
import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(".env")

API_KEY = os.getenv("SYNTHESIZER_API_KEY")
BASE_URL = os.getenv("SYNTHESIZER_BASE_URL")
MODEL = os.getenv("SYNTHESIZER_MODEL", "gemini-1.5-flash")

DEFAULT_CONCURRENCY = 16

PROMPT_TEMPLATE = """You are generating held-out evaluation questions for a fine-tuned cybersecurity model.

Given the Q&A pair below, write ONE new question that asks for the exact same fact, but with clearly different wording.

Requirements:
- The original answer must still be a complete, correct response to your new question.
- Do NOT mirror the original phrasing. Vary sentence structure, not just synonyms.
- Do NOT introduce new facts, assumptions, or external context not in the original.
- Preserve the original question's specificity. If it asked about a specific phase, mechanism, configuration, identifier, or relationship, your new question must target that same specific thing — do not generalize.
- Return ONLY the new question. No preamble, no quotes, no explanation.

Original question: {q}
Answer: {a}

New question:"""


_PREFIX_RE = re.compile(r"^\s*(?:[\*\-•]\s+|\d+[\.\)]\s+|new\s*:\s*)+", re.IGNORECASE)


def _clean(text: str) -> str:
    text = text.strip().strip('"').strip()
    text = _PREFIX_RE.sub("", text).strip()
    if text.lower().startswith("new question:"):
        text = text[len("new question:"):].strip()
    return text


async def _call(client: AsyncOpenAI, q: str, a: str, temperature: float) -> str:
    resp = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(q=q, a=a)}],
        max_tokens=2000,
        temperature=temperature,
    )
    choice = resp.choices[0]
    content = choice.message.content
    finish = getattr(choice, "finish_reason", None)
    if not content:
        raise RuntimeError(f"empty content (finish_reason={finish})")
    cleaned = _clean(content)
    if not cleaned:
        raise RuntimeError(f"content empty after cleaning (finish_reason={finish})")
    if finish == "length" or not cleaned.rstrip().endswith(("?", ".")):
        raise RuntimeError(f"truncated output (finish_reason={finish}): {cleaned[-40:]!r}")
    return cleaned


async def rewrite_one(client: AsyncOpenAI, sem: asyncio.Semaphore, q: str, a: str) -> str:
    async with sem:
        try:
            return await _call(client, q, a, temperature=0.8)
        except Exception as e1:
            try:
                return await _call(client, q, a, temperature=0.3)
            except Exception as e2:
                raise RuntimeError(f"both attempts failed: {e1} | retry: {e2}") from e2


def load_pairs(path: str) -> list[tuple[str, str]]:
    pairs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            convo = row["conversations"]
            q = next(m["value"] for m in convo if m["from"] == "human")
            a = next(m["value"] for m in convo if m["from"] == "gpt")
            pairs.append((q, a))
    return pairs


def default_output_for(input_path: str) -> str:
    p = Path(input_path)
    return str(p.with_name(f"{p.stem}_eval.jsonl"))


async def run(input_file: str, output_file: str, concurrency: int):
    assert API_KEY and BASE_URL, "SYNTHESIZER_API_KEY and SYNTHESIZER_BASE_URL must be set in .env"

    pairs = load_pairs(input_file)
    print(f"Loaded {len(pairs)} training pairs from {input_file}")
    print(f"Using model: {MODEL} | concurrency: {concurrency}")

    client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=120.0)
    sem = asyncio.Semaphore(concurrency)

    tasks = [rewrite_one(client, sem, q, a) for q, a in pairs]
    new_questions = await asyncio.gather(*tasks, return_exceptions=True)

    written = 0
    failed = 0
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as out:
        for (orig_q, a), new_q in zip(pairs, new_questions):
            if isinstance(new_q, Exception) or not new_q:
                failed += 1
                print(f"  [skip] {orig_q[:60]}... -> {new_q}")
                continue
            out.write(json.dumps({
                "conversations": [
                    {"from": "human", "value": new_q},
                    {"from": "gpt", "value": a},
                ]
            }, ensure_ascii=False) + "\n")
            written += 1

    print(f"\nWrote {written} eval pairs to {output_file}")
    if failed:
        print(f"Failed: {failed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input ShareGPT JSONL file",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path. Defaults to <input_stem>_eval.jsonl alongside the input.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Number of concurrent API requests (default: {DEFAULT_CONCURRENCY}).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    out = args.output or default_output_for(args.input)
    asyncio.run(run(args.input, out, args.concurrency))
