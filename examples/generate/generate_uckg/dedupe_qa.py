"""
dedupe_qa.py

Embedding-based deduplication for ShareGPT Q&A files.

Computes a sentence embedding per (question + answer), then for any pair whose
cosine similarity exceeds the threshold, keeps the first occurrence and drops
the rest. Writes a deduplicated JSONL alongside the input.

Usage:
    python3 examples/generate/generate_uckg/dedupe_qa.py \\
        --input examples/generate/generate_uckg/bluesmacking_5hop.jsonl \\
        --threshold 0.95
"""

import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_pairs(path: Path) -> list[tuple[str, str, dict]]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            q = next(m["value"] for m in row["conversations"] if m["from"] == "human")
            a = next(m["value"] for m in row["conversations"] if m["from"] == "gpt")
            out.append((q, a, row))
    return out


def dedupe(pairs: list[tuple[str, str, dict]], threshold: float, model_name: str) -> tuple[list[dict], list[tuple[int, int, float]]]:
    model = SentenceTransformer(model_name)
    texts = [f"Q: {q}\nA: {a}" for q, a, _ in pairs]
    print(f"Embedding {len(texts)} pairs with {model_name}...")
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True, batch_size=64)
    embs = np.asarray(embs, dtype=np.float32)

    print(f"Computing similarity matrix and filtering at threshold={threshold}...")
    sim = embs @ embs.T
    np.fill_diagonal(sim, 0.0)

    keep = np.ones(len(pairs), dtype=bool)
    drops: list[tuple[int, int, float]] = []
    for i in range(len(pairs)):
        if not keep[i]:
            continue
        dups = np.where((sim[i] >= threshold) & keep)[0]
        for j in dups:
            if j > i and keep[j]:
                keep[j] = False
                drops.append((i, int(j), float(sim[i, j])))

    kept = [pairs[i][2] for i in range(len(pairs)) if keep[i]]
    return kept, drops


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", default=None, help="Default: <input_stem>_dedup.jsonl")
    p.add_argument("--threshold", type=float, default=0.95)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--report", default=None, help="Optional path to write a CSV of dropped duplicates")
    args = p.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output) if args.output else in_path.with_name(f"{in_path.stem}_dedup.jsonl")

    pairs = load_pairs(in_path)
    print(f"Loaded {len(pairs)} pairs from {in_path}")

    kept, drops = dedupe(pairs, args.threshold, args.model)

    with open(out_path, "w", encoding="utf-8") as f:
        for row in kept:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    n_in = len(pairs)
    n_out = len(kept)
    print()
    print(f"Kept    {n_out:>5} / {n_in} ({100*n_out/n_in:.1f}%)")
    print(f"Dropped {n_in - n_out:>5} / {n_in} ({100*(n_in - n_out)/n_in:.1f}%)")
    print(f"Wrote   {out_path}")

    if args.report and drops:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write("kept_idx,dropped_idx,similarity,kept_q,dropped_q\n")
            for i, j, s in drops:
                kq = pairs[i][0].replace('"', "'")
                dq = pairs[j][0].replace('"', "'")
                f.write(f'{i},{j},{s:.4f},"{kq}","{dq}"\n')
        print(f"Report  {args.report}")


if __name__ == "__main__":
    main()
