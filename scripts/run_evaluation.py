#!/usr/bin/env python3
"""Single-model, single-prompt-level evaluation script."""

import argparse
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dataset import PhysReasonDataset
from src.evaluator import PhysicalReasoningAccuracy, BERTScoreMetric, ConservationLawViolationRate
from src.models import ModelRegistry
from src.pcs_scorer import PCSScorer
from src.prompts import PromptTemplate
from src.utils import ensure_dir, save_jsonl
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(description="Evaluate one LLM on PhysReason-800")
    parser.add_argument("--model", "-m", required=True, help="Model key (e.g., gpt-4o)")
    parser.add_argument("--prompt_level", "-p", required=True, help="P1–P9")
    parser.add_argument("--split", "-s", default="test", help="Dataset split")
    parser.add_argument("--tier", "-t", default="all", help="Tier filter")
    parser.add_argument("--dataset", "-d", default=None, help="Path to dataset JSON")
    parser.add_argument("--output_dir", "-o", required=True, help="Output directory")
    parser.add_argument("--n_calls", "-n", type=int, default=5, help="Calls per item")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    ensure_dir(args.output_dir)

    # Load components
    dataset = PhysReasonDataset(data_path=args.dataset, split=args.split, tier=args.tier, seed=args.seed)
    prompts = PromptTemplate()
    registry = ModelRegistry()
    model = registry.get_model(args.model)

    pra_scorer = PhysicalReasoningAccuracy()
    pcs_scorer = PCSScorer()
    clvr_checker = ConservationLawViolationRate()

    results = []
    pra_scores = []

    print(f"Evaluating {args.model} with {args.prompt_level} on {len(dataset)} items...")

    for item in tqdm(dataset.items):
        question = item["question"]
        gt = item["ground_truth"]

        # Render prompt
        prompt = prompts.render(args.prompt_level, question)

        # Generate
        responses = model.generate(
            system=prompt["system"],
            user=prompt["user"],
            n=args.n_calls,
        )

        # Score each response and average
        call_pra_scores = []
        call_pcs_scores = []
        call_clvr_flags = []

        for resp in responses:
            pra = pra_scorer.score(resp, gt)
            pcs = pcs_scorer.score(
                resp,
                expected_units=gt.get("unit"),
                check_energy=True,
                check_momentum=True,
                check_units=True,
            )
            clvr = clvr_checker.check_violation(resp, gt)

            call_pra_scores.append(pra)
            call_pcs_scores.append(pcs)
            call_clvr_flags.append(1.0 if clvr else 0.0)

        avg_pra = sum(call_pra_scores) / len(call_pra_scores)
        avg_pcs = sum(call_pcs_scores) / len(call_pcs_scores)
        avg_clvr = sum(call_clvr_flags) / len(call_clvr_flags)

        pra_scores.append(avg_pra)

        results.append({
            "id": item["id"],
            "tier": item["tier"],
            "prompt_level": args.prompt_level,
            "model": args.model,
            "responses": responses,
            "metrics": {
                "pra": round(avg_pra, 4),
                "pcs": round(avg_pcs, 4),
                "clvr": round(avg_clvr, 4),
            },
        })

    # Aggregate
    mean_pra = sum(pra_scores) / len(pra_scores) if pra_scores else 0
    summary = {
        "model": args.model,
        "prompt_level": args.prompt_level,
        "split": args.split,
        "tier": args.tier,
        "n_items": len(dataset),
        "n_calls_per_item": args.n_calls,
        "mean_pra": round(mean_pra, 4),
        "results": results,
    }

    out_path = Path(args.output_dir) / f"{args.model}_{args.prompt_level}_{args.split}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Done. Mean PRA: {mean_pra:.3f}. Saved to {out_path}")


if __name__ == "__main__":
    main()
