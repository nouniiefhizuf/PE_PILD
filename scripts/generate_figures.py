#!/usr/bin/env python3
"""Reproduce all paper figures from raw results."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.3)


def load_results(results_dir: str) -> pd.DataFrame:
    """Load all result JSONs into a DataFrame."""
    records = []
    for path in Path(results_dir).glob("*.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for r in data.get("results", []):
            records.append({
                "model": data["model"],
                "prompt_level": data["prompt_level"],
                "tier": r["tier"],
                "pra": r["metrics"]["pra"],
                "pcs": r["metrics"]["pcs"],
                "clvr": r["metrics"]["clvr"],
            })
    return pd.DataFrame(records)


def fig_taxonomy_arrow(df: pd.DataFrame, output_dir: Path):
    """Figure 2: P1–P9 taxonomy with mean PRA arrow."""
    mean_pra = df.groupby("prompt_level")["pra"].mean().reindex([f"P{i}" for i in range(1, 10)])

    fig, ax = plt.subplots(figsize=(10, 4))
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, 9))

    x = np.arange(9)
    bars = ax.bar(x, mean_pra.values * 100, color=colors, edgecolor="black", linewidth=0.5)

    # Arrow annotation
    ax.annotate(
        f"PRA: {mean_pra.iloc[0]*100:.1f}% → {mean_pra.iloc[-1]*100:.1f}%",
        xy=(0, mean_pra.iloc[0] * 100),
        xytext=(8, mean_pra.iloc[-1] * 100),
        arrowprops=dict(arrowstyle="->", color="navy", lw=2),
        fontsize=12,
        color="navy",
        ha="center",
    )

    ax.set_xticks(x)
    ax.set_xticklabels([f"P{i}" for i in range(1, 10)])
    ax.set_ylabel("PRA (%)")
    ax.set_xlabel("Prompt Level")
    ax.set_ylim(0, 100)
    ax.set_title("P1–P9 Prompt Taxonomy: Mean PRA Across All Models")

    plt.tight_layout()
    plt.savefig(output_dir / "fig2_taxonomy_arrow.pdf", dpi=300)
    plt.savefig(output_dir / "fig2_taxonomy_arrow.png", dpi=300)
    plt.close()


def fig_tier_curves(df: pd.DataFrame, output_dir: Path):
    """Figure 3: PRA by difficulty tier."""
    pivot = df.groupby(["tier", "prompt_level"])["pra"].mean().unstack()
    pivot = pivot.reindex(columns=[f"P{i}" for i in range(1, 10)])

    fig, ax = plt.subplots(figsize=(8, 5))
    markers = ["s", "^", "o", "D"]
    tiers = ["Tier-1", "Tier-2", "Tier-3", "Tier-4"]

    for i, tier in enumerate(tiers):
        if tier in pivot.index:
            ax.plot(range(9), pivot.loc[tier].values * 100, marker=markers[i], label=tier, linewidth=2)

    ax.set_xticks(range(9))
    ax.set_xticklabels([f"P{i}" for i in range(1, 10)])
    ax.set_ylabel("PRA (%)")
    ax.set_xlabel("Prompt Level")
    ax.legend(title="Tier")
    ax.set_ylim(0, 100)
    ax.set_title("PRA by Difficulty Tier (Averaged Over All Models)")

    plt.tight_layout()
    plt.savefig(output_dir / "fig3_tier_curves.pdf", dpi=300)
    plt.savefig(output_dir / "fig3_tier_curves.png", dpi=300)
    plt.close()


def fig_model_comparison(df: pd.DataFrame, output_dir: Path):
    """Figure 4: Bar chart P1 vs P7 vs P9 by model."""
    sub = df[df["prompt_level"].isin(["P1", "P7", "P9"])]
    pivot = sub.groupby(["model", "prompt_level"])["pra"].mean().unstack()

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(pivot.index))
    width = 0.25

    colors = {"P1": "#cccccc", "P7": "#9999ff", "P9": "#3333cc"}
    for i, p in enumerate(["P1", "P7", "P9"]):
        if p in pivot.columns:
            ax.bar(x + (i - 1) * width, pivot[p].values * 100, width, label=p, color=colors[p])

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, rotation=15, ha="right")
    ax.set_ylabel("PRA (%)")
    ax.legend(title="Prompt Level")
    ax.set_ylim(0, 100)
    ax.set_title("PRA by Model at P1, P7, and P9")

    plt.tight_layout()
    plt.savefig(output_dir / "fig4_model_comparison.pdf", dpi=300)
    plt.savefig(output_dir / "fig4_model_comparison.png", dpi=300)
    plt.close()


def fig_heatmap(df: pd.DataFrame, model: str, output_dir: Path):
    """Figure 5-style heatmap: pairwise Wilcoxon p-values."""
    from scipy.stats import wilcoxon
    from statsmodels.stats.multitest import multipletests

    sub = df[df["model"] == model]
    levels = [f"P{i}" for i in range(1, 10)]
    scores = [sub[sub["prompt_level"] == p]["pra"].values for p in levels]

    n = len(levels)
    pmat = np.ones((n, n))
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            try:
                _, p = wilcoxon(scores[i], scores[j], alternative="greater")
            except ValueError:
                p = 1.0
            pmat[i, j] = p
            pairs.append((i, j, p))

    if pairs:
        all_p = [x[2] for x in pairs]
        _, corr, _, _ = multipletests(all_p, method="holm")
        for k, (i, j, _) in enumerate(pairs):
            pmat[i, j] = corr[k]

    fig, ax = plt.subplots(figsize=(8, 7))
    cmap = sns.color_palette("Blues", as_cmap=True)
    mask = np.tril(np.ones_like(pmat, dtype=bool), k=0)

    sns.heatmap(
        pmat,
        mask=mask,
        annot=True,
        fmt=".3f",
        cmap=cmap,
        vmin=0,
        vmax=0.05,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8, "label": "p-value"},
        ax=ax,
    )
    ax.set_xticklabels(levels)
    ax.set_yticklabels(levels, rotation=0)
    ax.set_title(f"Pairwise Wilcoxon p-values ({model})")

    plt.tight_layout()
    plt.savefig(output_dir / f"fig5_heatmap_{model.replace('-', '_')}.pdf", dpi=300)
    plt.savefig(output_dir / f"fig5_heatmap_{model.replace('-', '_')}.png", dpi=300)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Generate paper figures")
    parser.add_argument("--results_dir", "-r", required=True, help="Directory with result JSONs")
    parser.add_argument("--output_dir", "-o", required=True, help="Figure output directory")
    args = parser.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    df = load_results(args.results_dir)
    if df.empty:
        print("No results found. Run benchmark first.")
        return

    print("Generating Figure 2 (taxonomy arrow)...")
    fig_taxonomy_arrow(df, out)

    print("Generating Figure 3 (tier curves)...")
    fig_tier_curves(df, out)

    print("Generating Figure 4 (model comparison)...")
    fig_model_comparison(df, out)

    print("Generating Figure 5-style heatmaps...")
    for model in df["model"].unique():
        fig_heatmap(df, model, out)

    print(f"All figures saved to {out}")


if __name__ == "__main__":
    main()
