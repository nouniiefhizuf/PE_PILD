#!/usr/bin/env python3
"""Compute ANOVA, Wilcoxon tests, and effect sizes."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests


def load_all(results_dir: str) -> pd.DataFrame:
    records = []
    for path in Path(results_dir).glob("*.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for r in data.get("results", []):
            records.append({
                "model": data["model"],
                "prompt_level": data["prompt_level"],
                "item_id": r["id"],
                "tier": r["tier"],
                "pra": r["metrics"]["pra"],
            })
    return pd.DataFrame(records)


def pairwise_wilcoxon(df: pd.DataFrame, model: str) -> pd.DataFrame:
    """Compute Holm-Bonferroni corrected Wilcoxon matrix for one model."""
    sub = df[df["model"] == model]
    levels = sorted(sub["prompt_level"].unique(), key=lambda x: int(x[1:]))

    # Build score matrix: rows = prompts, cols = items
    items = sorted(sub["item_id"].unique())
    scores = np.full((len(levels), len(items)), np.nan)
    level_idx = {p: i for i, p in enumerate(levels)}
    item_idx = {it: j for j, it in enumerate(items)}

    for _, row in sub.iterrows():
        i = level_idx[row["prompt_level"]]
        j = item_idx[row["item_id"]]
        scores[i, j] = row["pra"]

    # Drop items with any missing (shouldn't happen if complete)
    valid_cols = ~np.isnan(scores).any(axis=0)
    scores = scores[:, valid_cols]

    n = len(levels)
    pmat = np.full((n, n), np.nan)
    rmat = np.full((n, n), np.nan)
    pairs = []

    for i in range(n):
        for j in range(i + 1, n):
            try:
                diff = scores[i] - scores[j]
                # Remove zeros for Wilcoxon
                diff = diff[diff != 0]
                if len(diff) == 0:
                    p = 1.0
                    r_eff = 0.0
                else:
                    stat, p = wilcoxon(diff, alternative="greater")
                    r_eff = stat / np.sqrt(len(diff)) if len(diff) > 0 else 0.0
            except Exception:
                p = 1.0
                r_eff = 0.0
            pmat[i, j] = p
            pairs.append((i, j, p))
            rmat[i, j] = r_eff

    # Holm-Bonferroni
    if pairs:
        all_p = [x[2] for x in pairs]
        _, corr, _, _ = multipletests(all_p, method="holm")
        for k, (i, j, _) in enumerate(pairs):
            pmat[i, j] = corr[k]

    # Build DataFrame
    p_df = pd.DataFrame(pmat, index=levels, columns=levels)
    r_df = pd.DataFrame(rmat, index=levels, columns=levels)
    return p_df, r_df


def main():
    parser = argparse.ArgumentParser(description="Compute statistics")
    parser.add_argument("--input_dir", "-i", required=True, help="Results directory")
    parser.add_argument("--output_dir", "-o", required=True, help="Output tables directory")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    df = load_all(args.input_dir)
    if df.empty:
        print("No data found.")
        return

    # Per-model Wilcoxon matrices
    for model in df["model"].unique():
        print(f"Processing {model}...")
        p_df, r_df = pairwise_wilcoxon(df, model)
        p_df.to_csv(Path(args.output_dir) / f"wilcoxon_p_{model}.csv")
        r_df.to_csv(Path(args.output_dir) / f"wilcoxon_r_{model}.csv")

    # Summary table: mean PRA per model × prompt
    summary = df.groupby(["model", "prompt_level"])["pra"].agg(["mean", "std", "count"]).reset_index()
    summary.to_csv(Path(args.output_dir) / "summary_pra.csv", index=False)

    # Tier-wise summary
    tier_summary = df.groupby(["tier", "prompt_level"])["pra"].mean().unstack()
    tier_summary.to_csv(Path(args.output_dir) / "summary_tier.csv")

    print(f"Tables saved to {args.output_dir}")


if __name__ == "__main__":
    main()
