"""
visualize_dataflow.py

Draws the eval data flow diagram:
  Training pair -> (rephrase question) -> Eval pair -> (model predicts)
  -> Prediction -> (judge compares) -> Scores

Uses a concrete worst-case row from the 1-hop eval judged file so the
diagram shows a real example, not a placeholder.

Usage:
    python3 examples/generate/generate_uckg/visualize_dataflow.py
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

BASE = Path("examples/generate/generate_uckg")
JUDGED = BASE / "eval_1hop_eval_results_judged.jsonl"
OUTPUT = BASE / "dataflow_diagram.png"

TRAIN_COLOR = "#5B8DEF"
EVAL_COLOR = "#F59E42"
PRED_COLOR = "#A78BFA"
JUDGE_COLOR = "#10B981"
TEXT_COLOR = "#2E3440"
MUTED = "#8A94A6"
LABEL_COLOR = "#6B7280"
BG = "#FBFBFD"
BOX_BG = "#FFFFFF"


def pick_example() -> dict:
    rows = [json.loads(l) for l in open(JUDGED)]
    severity = next(
        r for r in rows
        if "severity" in r["question"].lower() and "classif" in r["question"].lower()
    )
    return {
        "q_train": "What is the severity of the BlueSmacking attack?",
        "a_train": "Medium Severity",
        "q_eval": "How is the BlueSmacking severity classified?",
        "a_eval": "Medium Severity",
        "prediction": "Classified as a Low-Severity threat.",
        "relevance": severity["relevance"],
        "completeness": severity["completeness"],
        "accuracy": severity["accuracy"],
        "specificity": severity["specificity"],
        "clarity": severity["clarity"],
    }


def box(ax, x, y, w, h, title, lines, color):
    header_h = 0.45
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.10",
        facecolor=BOX_BG, edgecolor=color, linewidth=1.8, zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (x, y + h - header_h), w, header_h,
        boxstyle="round,pad=0.015,rounding_size=0.10",
        facecolor=color, edgecolor=color, linewidth=0, zorder=3,
    ))
    ax.text(
        x + w / 2, y + h - header_h / 2, title,
        ha="center", va="center",
        fontsize=11, fontweight="700", color="white", zorder=4,
    )

    text_y = y + h - header_h - 0.28
    for label, value in lines:
        ax.text(
            x + 0.20, text_y, label,
            ha="left", va="top",
            fontsize=9, color=LABEL_COLOR, fontweight="600", zorder=4,
        )
        ax.text(
            x + 0.20, text_y - 0.28, value,
            ha="left", va="top",
            fontsize=10, color=TEXT_COLOR, zorder=4,
        )
        text_y -= 0.72


def code_box(ax, x, y, w, h, title, body, color):
    header_h = 0.45
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.10",
        facecolor=BOX_BG, edgecolor=color, linewidth=1.8, zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (x, y + h - header_h), w, header_h,
        boxstyle="round,pad=0.015,rounding_size=0.10",
        facecolor=color, edgecolor=color, linewidth=0, zorder=3,
    ))
    ax.text(
        x + w / 2, y + h - header_h / 2, title,
        ha="center", va="center",
        fontsize=11, fontweight="700", color="white", zorder=4,
    )

    ax.add_patch(FancyBboxPatch(
        (x + 0.20, y + 0.20), w - 0.40, h - header_h - 0.40,
        boxstyle="round,pad=0.01,rounding_size=0.04",
        facecolor="#F3F4F6", edgecolor="#E5E7EB", linewidth=0.8, zorder=3,
    ))
    ax.text(
        x + 0.32, y + h - header_h - 0.18, body,
        ha="left", va="top",
        fontsize=8.5, color=TEXT_COLOR, zorder=4,
        family="monospace",
    )


def arrow(ax, x1, y1, x2, y2, label=None, color=MUTED):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=20,
        color=color, linewidth=2.0, zorder=1,
    ))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(
            mx, my, label,
            ha="center", va="center",
            fontsize=9, color=TEXT_COLOR, style="italic",
            bbox=dict(facecolor=BG, edgecolor="none", pad=3),
            zorder=5,
        )


def main():
    ex = pick_example()

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.facecolor": BG,
        "savefig.facecolor": BG,
    })

    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 12)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(BG)

    fig.text(
        0.5, 0.95,
        "Held-Out Evaluation Data Flow",
        ha="center", fontsize=18, fontweight="700", color=TEXT_COLOR,
    )
    fig.text(
        0.5, 0.915,
        "Same ground-truth answer, rephrased question — tests generalization, not memorization",
        ha="center", fontsize=11, color=MUTED,
    )

    box(
        ax, 0.5, 8.2, 6.0, 2.8,
        "1.  TRAINING PAIR  (seen by model)",
        [
            ("Q_train", ex["q_train"]),
            ("A_train", ex["a_train"]),
        ],
        TRAIN_COLOR,
    )

    box(
        ax, 8.5, 8.2, 6.0, 2.8,
        "2.  EVAL PAIR  (held-out, unseen)",
        [
            ("Q_eval  (NEW phrasing)", ex["q_eval"]),
            ("A_eval  (same as A_train)", ex["a_eval"]),
        ],
        EVAL_COLOR,
    )

    arrow(ax, 6.5, 9.6, 8.5, 9.6, label="rephrase Q only\nkeep A identical")

    box(
        ax, 4.5, 4.6, 6.0, 2.4,
        "3.  MODEL PREDICTION",
        [
            ("Fine-tuned model answers Q_eval", ex["prediction"]),
        ],
        PRED_COLOR,
    )

    arrow(ax, 11.5, 8.2, 8.5, 7.0, label="vLLM\ninference")

    judge_prompt = (
        "You are an expert cybersecurity evaluator. Score the MODEL\n"
        "ANSWER against the REFERENCE ANSWER on five dimensions, 0-10:\n"
        "\n"
        "  1. Relevance     - does it address the question?\n"
        "  2. Completeness  - does it cover key facts from reference?\n"
        "  3. Accuracy      - are factual claims correct? Contradicting\n"
        "                     the reference counts as accuracy failure.\n"
        "  4. Specificity   - concrete IDs, names, values, mechanisms?\n"
        "  5. Clarity       - structured, unambiguous, readable?\n"
        "\n"
        "Paraphrasing is fine. Do NOT penalize different wording.\n"
        "\n"
        "QUESTION:   How is the BlueSmacking severity classified?\n"
        "REFERENCE:  Medium Severity\n"
        "MODEL:      Classified as a Low-Severity threat."
    )
    code_box(
        ax, 1.5, 0.2, 12.0, 3.6,
        "4.  LLM JUDGE  (prompt sent to Gemini)",
        judge_prompt,
        JUDGE_COLOR,
    )

    arrow(ax, 7.5, 4.6, 7.5, 3.9)

    fig.savefig(OUTPUT, dpi=180, bbox_inches="tight", facecolor=BG)
    print(f"Saved diagram to {OUTPUT}")


if __name__ == "__main__":
    main()
