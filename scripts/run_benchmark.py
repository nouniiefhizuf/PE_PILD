#!/usr/bin/env python3
"""Full benchmark: P1–P9 × all models."""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_single(model: str, prompt: str, split: str, dataset: str, output_dir: str, n_calls: int):
    cmd = [
        sys.executable,
        "scripts/run_evaluation.py",
        "--model", model,
        "--prompt_level", prompt,
        "--split", split,
        "--dataset", dataset,
        "--output_dir", output_dir,
        "--n_calls", str(n_calls),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return model, prompt, result.returncode, result.stdout, result.stderr


def main():
    parser = argparse.ArgumentParser(description="Run full PhysReason-800 benchmark")
    parser.add_argument("--models", "-m", nargs="+", default=["gpt-4o", "claude-3.5", "gemini-1.5", "llama-3-70b", "mixtral-8x22b"])
    parser.add_argument("--prompt_levels", "-p", nargs="+", default=[f"P{i}" for i in range(1, 10)])
    parser.add_argument("--dataset", "-d", default="data/physreason800.json")
    parser.add_argument("--output_dir", "-o", default="results/raw/")
    parser.add_argument("--split", "-s", default="test")
    parser.add_argument("--n_calls", "-n", type=int, default=5)
    parser.add_argument("--max_workers", type=int, default=3, help="Concurrent API calls")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    tasks = []
    for model in args.models:
        for prompt in args.prompt_levels:
            tasks.append((model, prompt))

    print(f"Running {len(tasks)} configurations ({len(args.models)} models × {len(args.prompt_levels)} prompts)...")

    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(run_single, m, p, args.split, args.dataset, args.output_dir, args.n_calls): (m, p)
            for m, p in tasks
        }
        for future in as_completed(futures):
            model, prompt, rc, stdout, stderr = future.result()
            if rc == 0:
                print(f"  ✓ {model} / {prompt}")
            else:
                print(f"  ✗ {model} / {prompt} failed")
                print(stderr[:200])

    print(f"\nAll results saved to {args.output_dir}")


if __name__ == "__main__":
    main()
