"""
visualize_eval.py

Builds a 2-panel dashboard comparing fine-tuned model performance on training
vs. held-out eval sets, across two scoring systems:
  - ROUGE/BLEU (n-gram overlap)
  - LLM Judge (5 dimensions, 0-10)

Usage:
    python3 examples/generate/generate_uckg/visualize_eval.py                # defaults to 1hop
    python3 examples/generate/generate_uckg/visualize_eval.py --hop 2hop
"""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

BASE = Path("examples/generate/generate_uckg")

DIMENSIONS = ["relevance", "completeness", "accuracy", "specificity", "clarity"]
ROUGE_METRICS = ["predict_bleu-4", "predict_rouge-1", "predict_rouge-2", "predict_rouge-l"]
ROUGE_LABELS = ["BLEU-4", "ROUGE-1", "ROUGE-2", "ROUGE-L"]

TRAIN_COLOR = "#5B8DEF"
EVAL_COLOR = "#F59E42"
TRAIN_FILL = "#5B8DEF"
EVAL_FILL = "#F59E42"
TEXT_COLOR = "#2E3440"
MUTED = "#8A94A6"
BG = "#FBFBFD"


def load_rouge(path: Path) -> list[float]:
    with open(path) as f:
        data = json.load(f)
    return [data[m] for m in ROUGE_METRICS]


def load_judged(path: Path) -> dict:
    per_dim: dict[str, list[int]] = {d: [] for d in DIMENSIONS}
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            for d in DIMENSIONS:
                per_dim[d].append(row[d])
    return per_dim


def avg(per_dim: dict) -> list[float]:
    return [float(np.mean(per_dim[d])) for d in DIMENSIONS]


def style_axes(ax):
    for spine_name in ("top", "right"):
        ax.spines[spine_name].set_visible(False)
    for spine_name in ("left", "bottom"):
        ax.spines[spine_name].set_color(MUTED)
        ax.spines[spine_name].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, length=0)
    ax.set_facecolor(BG)


def panel_rouge(ax, train_vals, eval_vals):
    x = np.arange(len(ROUGE_LABELS))
    w = 0.36
    bars_t = ax.bar(
        x - w / 2, train_vals, w,
        label="Train", color=TRAIN_COLOR, edgecolor="white", linewidth=0.8,
    )
    bars_e = ax.bar(
        x + w / 2, eval_vals, w,
        label="Eval", color=EVAL_COLOR, edgecolor="white", linewidth=0.8,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(ROUGE_LABELS, fontsize=10, color=TEXT_COLOR)
    ax.set_ylabel("Score (0–100)", fontsize=10, color=TEXT_COLOR)
    ax.set_title(
        "N-gram overlap metrics  ·  BLEU / ROUGE",
        fontsize=13, fontweight="600", color=TEXT_COLOR,
        loc="left", pad=14,
    )
    ax.set_ylim(0, 100)
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color="#E5E7EB", zorder=0)
    ax.set_axisbelow(True)
    style_axes(ax)

    legend = ax.legend(
        loc="upper right", frameon=False, fontsize=10,
        labelcolor=TEXT_COLOR,
    )
    for handle in legend.legend_handles:
        handle.set_edgecolor("white")

    for bars, vals in ((bars_t, train_vals), (bars_e, eval_vals)):
        for bar, v in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2, v + 2,
                f"{v:.1f}",
                ha="center", va="bottom",
                fontsize=9, color=TEXT_COLOR, fontweight="500",
            )


def panel_radar(ax, train_avg, eval_avg):
    n = len(DIMENSIONS)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    t = train_avg + train_avg[:1]
    e = eval_avg + eval_avg[:1]

    ax.set_facecolor(BG)

    ax.fill(angles, e, alpha=0.20, color=EVAL_FILL, zorder=2)
    ax.plot(angles, e, "-", linewidth=2.2, color=EVAL_COLOR, label="Eval", zorder=4)
    ax.scatter(angles, e, s=42, color=EVAL_COLOR, zorder=5, edgecolor="white", linewidth=1.2)

    ax.fill(angles, t, alpha=0.18, color=TRAIN_FILL, zorder=3)
    ax.plot(angles, t, "-", linewidth=2.2, color=TRAIN_COLOR, label="Train", zorder=4)
    ax.scatter(angles, t, s=42, color=TRAIN_COLOR, zorder=5, edgecolor="white", linewidth=1.2)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(
        [d.capitalize() for d in DIMENSIONS],
        fontsize=10, color=TEXT_COLOR,
    )
    ax.tick_params(axis="x", pad=12)

    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(["2", "4", "6", "8", "10"], fontsize=8, color=MUTED)
    ax.set_rlabel_position(45)

    ax.grid(True, color="#E5E7EB", linewidth=0.7)
    ax.spines["polar"].set_color("#E5E7EB")
    ax.spines["polar"].set_linewidth(0.8)

    ax.text(
        -0.15, 1.15,
        "LLM-Judge dimension profile  ·  Semantic evaluation (0–10)",
        transform=ax.transAxes, fontsize=13, fontweight="600", color=TEXT_COLOR,
    )

    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.22, 1.10),
        frameon=False,
        fontsize=10,
        labelcolor=TEXT_COLOR,
    )


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--hop", default="1hop", help="hop prefix, e.g. 1hop, 2hop")
    p.add_argument("--split", action="store_true", help="save each panel as its own PNG")
    return p.parse_args()


def main():
    args = parse_args()
    hop = args.hop

    train_scores = BASE / f"eval_{hop}_train_scores.json"
    eval_scores = BASE / f"eval_{hop}_eval_scores.json"
    train_judged = BASE / f"eval_{hop}_train_results_judged.jsonl"
    eval_judged = BASE / f"eval_{hop}_eval_results_judged.jsonl"

    train_rouge = load_rouge(train_scores)
    eval_rouge = load_rouge(eval_scores)
    train_per_dim = load_judged(train_judged)
    eval_per_dim = load_judged(eval_judged)
    train_avg = avg(train_per_dim)
    eval_avg = avg(eval_per_dim)

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titleweight": "600",
        "axes.labelcolor": TEXT_COLOR,
        "axes.edgecolor": MUTED,
        "figure.facecolor": BG,
        "savefig.facecolor": BG,
    })

    overall_train = float(np.mean(train_avg))
    overall_eval = float(np.mean(eval_avg))
    hop_label = hop.replace("hop", "-Hop").capitalize()

    if args.split:
        # --- panel 1: BLEU/ROUGE bars ---
        fig1 = plt.figure(figsize=(9, 8))
        gs1 = fig1.add_gridspec(1, 1, left=0.12, right=0.95, top=0.76, bottom=0.12)
        ax1 = fig1.add_subplot(gs1[0, 0])
        panel_rouge(ax1, train_rouge, eval_rouge)
        fig1.text(
            0.10, 0.93,
            f"{hop_label} — N-gram Overlap (BLEU / ROUGE)",
            fontsize=17, fontweight="700", color=TEXT_COLOR,
        )
        fig1.text(
            0.10, 0.885,
            "Train vs. held-out eval  ·  scores 0–100",
            fontsize=11, color=MUTED,
        )
        out1 = BASE / f"{hop}_dashboard_rouge.png"
        fig1.savefig(out1, dpi=180, bbox_inches="tight", facecolor=BG)
        print(f"Saved bar-chart dashboard to {out1}")

        # --- panel 2: LLM-Judge radar ---
        fig2 = plt.figure(figsize=(9, 8))
        gs2 = fig2.add_gridspec(1, 1, left=0.10, right=0.90, top=0.76, bottom=0.10)
        ax2 = fig2.add_subplot(gs2[0, 0], projection="polar")
        panel_radar(ax2, train_avg, eval_avg)
        fig2.text(
            0.10, 0.93,
            f"{hop_label} — LLM-Judge Semantic Evaluation",
            fontsize=17, fontweight="700", color=TEXT_COLOR,
        )
        fig2.text(
            0.10, 0.885,
            f"Overall    Train  {overall_train:.2f} / 10     |     Eval  {overall_eval:.2f} / 10",
            fontsize=11, color=MUTED,
        )
        out2 = BASE / f"{hop}_dashboard_judge.png"
        fig2.savefig(out2, dpi=180, bbox_inches="tight", facecolor=BG)
        print(f"Saved radar dashboard to {out2}")
        return

    # --- combined 2-panel layout (default) ---
    output_image = BASE / f"{hop}_dashboard.png"
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(1, 2, wspace=0.45, left=0.08, right=0.94, top=0.76, bottom=0.12)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1], projection="polar")

    panel_rouge(ax1, train_rouge, eval_rouge)
    panel_radar(ax2, train_avg, eval_avg)

    fig.text(
        0.07, 0.93,
        f"{hop_label} — Fine-tuned Model Evaluation",
        fontsize=18, fontweight="700", color=TEXT_COLOR,
    )
    fig.text(
        0.07, 0.885,
        f"LLM-Judge overall    Train  {overall_train:.2f} / 10     |     Eval  {overall_eval:.2f} / 10",
        fontsize=11, color=MUTED,
    )

    fig.savefig(output_image, dpi=180, bbox_inches="tight", facecolor=BG)
    print(f"Saved dashboard to {output_image}")


if __name__ == "__main__":
    main()
