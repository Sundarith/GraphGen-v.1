"""
visualize_crosshop.py

Cross-hop comparison dashboard. Loads judged JSONL files for hops 1..5 (both
train and eval splits) and renders:

  Panel A : line plot of LLM-Judge overall score vs hop depth (train + eval).
  Panel B : grouped bar chart of the 5 LLM-Judge dimensions across hops (eval).
  Panel C : table of train/eval overall + n per hop.

Usage:
    python3 examples/generate/generate_uckg/visualize_crosshop.py
"""

import json
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np

BASE = Path("examples/generate/generate_uckg")
OUT  = BASE / "crosshop_dashboard.png"

HOPS = ["1hop", "2hop", "3hop", "4hop", "5hop"]
HOP_LABELS = ["1-Hop", "2-Hop", "3-Hop", "4-Hop", "5-Hop"]
DIMS = ["relevance", "completeness", "accuracy", "specificity", "clarity"]
DIM_LABELS = ["Relevance", "Completeness", "Accuracy", "Specificity", "Clarity"]

TRAIN_COLOR = "#5B8DEF"
EVAL_COLOR  = "#F59E42"
TEXT_COLOR  = "#2E3440"
MUTED       = "#8A94A6"
BG          = "#FBFBFD"
DIM_PALETTE = ["#5B8DEF", "#F59E42", "#A78BFA", "#10B981", "#EF4444"]


def load(hop: str, split: str) -> dict:
    rows = [json.loads(l) for l in open(BASE / f"eval_{hop}_{split}_results_judged.jsonl")]
    per_dim = {d: mean(r[d] for r in rows) for d in DIMS}
    overall = mean(per_dim.values())
    return {"per_dim": per_dim, "overall": overall, "n": len(rows)}


def style_axes(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, length=0)
    ax.set_facecolor(BG)


def panel_overall(ax, train, eval_):
    x = np.arange(len(HOPS))
    t_overall = [train[h]["overall"] for h in HOPS]
    e_overall = [eval_[h]["overall"] for h in HOPS]

    ax.plot(x, t_overall, "-o", color=TRAIN_COLOR, linewidth=2.4,
            markersize=8, markeredgecolor="white", markeredgewidth=1.5,
            label="Train")
    ax.plot(x, e_overall, "-o", color=EVAL_COLOR, linewidth=2.4,
            markersize=8, markeredgecolor="white", markeredgewidth=1.5,
            label="Eval")

    for i, (t, e) in enumerate(zip(t_overall, e_overall)):
        ax.text(i, t + 0.07, f"{t:.2f}", ha="center", fontsize=9,
                color=TRAIN_COLOR, fontweight="600")
        ax.text(i, e - 0.18, f"{e:.2f}", ha="center", fontsize=9,
                color=EVAL_COLOR, fontweight="600")

    ax.set_xticks(x)
    ax.set_xticklabels(HOP_LABELS, fontsize=10, color=TEXT_COLOR)
    ax.set_ylim(8.4, 10.15)
    ax.set_ylabel("LLM-Judge overall (0–10)", fontsize=10, color=TEXT_COLOR)
    ax.set_title(
        "Overall semantic quality across hop depth",
        fontsize=13, fontweight="600", color=TEXT_COLOR, loc="left", pad=14,
    )
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color="#E5E7EB", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", frameon=False, fontsize=10, labelcolor=TEXT_COLOR)
    style_axes(ax)


def panel_dims(ax, eval_):
    x = np.arange(len(HOPS))
    w = 0.16

    for i, (d, label, color) in enumerate(zip(DIMS, DIM_LABELS, DIM_PALETTE)):
        vals = [eval_[h]["per_dim"][d] for h in HOPS]
        offset = (i - 2) * w
        bars = ax.bar(x + offset, vals, w, color=color, edgecolor="white",
                      linewidth=0.6, label=label)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.05,
                    f"{v:.1f}", ha="center", va="bottom",
                    fontsize=7.5, color=TEXT_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels(HOP_LABELS, fontsize=10, color=TEXT_COLOR)
    ax.set_ylim(7.5, 10.6)
    ax.set_ylabel("Score (0–10)", fontsize=10, color=TEXT_COLOR)
    ax.set_title(
        "Eval-side dimension breakdown across hop depth",
        fontsize=13, fontweight="600", color=TEXT_COLOR, loc="left", pad=14,
    )
    ax.yaxis.grid(True, linestyle="-", linewidth=0.6, color="#E5E7EB", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=5,
        frameon=False, fontsize=9, labelcolor=TEXT_COLOR,
    )
    style_axes(ax)


def panel_table(ax, train, eval_):
    ax.axis("off")
    ax.set_facecolor(BG)

    headers = ["Hop", "n (eval)", "Train", "Eval", "Δ (E−T)"]
    rows = []
    for hop, label in zip(HOPS, HOP_LABELS):
        n = eval_[hop]["n"]
        t = train[hop]["overall"]
        e = eval_[hop]["overall"]
        rows.append([label, f"{n:,}", f"{t:.2f}", f"{e:.2f}", f"{e - t:+.2f}"])

    tbl = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        loc="center",
        colColours=["#EEF2F7"] * len(headers),
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 1.7)

    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#E5E7EB")
        cell.set_linewidth(0.7)
        if r == 0:
            cell.set_text_props(color=TEXT_COLOR, fontweight="700")
        else:
            cell.set_text_props(color=TEXT_COLOR)
            if c == 4:
                delta = float(rows[r - 1][4])
                cell.set_text_props(
                    color="#10B981" if delta >= 0 else "#EF4444",
                    fontweight="600",
                )

    ax.set_title(
        "Train vs Eval overall, per hop",
        fontsize=13, fontweight="600", color=TEXT_COLOR, loc="left", pad=18,
    )


def main():
    train = {h: load(h, "train") for h in HOPS}
    eval_ = {h: load(h, "eval")  for h in HOPS}

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titleweight": "600",
        "figure.facecolor": BG,
        "savefig.facecolor": BG,
    })

    fig = plt.figure(figsize=(17, 11))
    gs = fig.add_gridspec(
        2, 2, height_ratios=[1.0, 0.85],
        wspace=0.30, hspace=0.55,
        left=0.06, right=0.97, top=0.86, bottom=0.07,
    )

    ax_overall = fig.add_subplot(gs[0, 0])
    ax_table   = fig.add_subplot(gs[0, 1])
    ax_dims    = fig.add_subplot(gs[1, :])

    panel_overall(ax_overall, train, eval_)
    panel_table(ax_table, train, eval_)
    panel_dims(ax_dims, eval_)

    fig.text(
        0.06, 0.94,
        "Cross-Hop Evaluation Summary",
        fontsize=20, fontweight="700", color=TEXT_COLOR,
    )
    fig.text(
        0.06, 0.905,
        "Fine-tuned model · LLM-Judge (Gemini) on train (seen Q) and held-out eval (rephrased Q) splits",
        fontsize=11, color=MUTED,
    )

    fig.savefig(OUT, dpi=180, bbox_inches="tight", facecolor=BG)
    print(f"Saved cross-hop dashboard to {OUT}")


if __name__ == "__main__":
    main()
