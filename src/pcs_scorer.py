"""Physical Consistency Score (PCS) implementation."""

import re
import sys
from typing import Dict, List, Optional


class PCSScorer:
    """
    Physical Consistency Score (PCS).

    Heuristic that parses model output for three markers:
    1. Energy balance equation present (+1)
    2. Momentum conservation stated or used (+1)
    3. Final answer has correct units (+1)

    PCS ∈ [0, 1], normalized over active markers.
    """

    def __init__(self, active_markers: Optional[List[str]] = None):
        """
        Args:
            active_markers: Subset of ['energy', 'momentum', 'units'] to check.
                            If None, all three are active.
        """
        self.markers = active_markers or ["energy", "momentum", "units"]
        self.energy_regex = re.compile(
            r'(?:conservation of energy|energy balance|KE\s*\+\s*PE|'
            r'½\s*m\s*v\^2\s*\+\s*m\s*g\s*h|'
            r'E_total\s*=\s*constant)',
            re.IGNORECASE,
        )
        self.momentum_regex = re.compile(
            r'(?:conservation of momentum|momentum is conserved|'
            r'p\s*=\s*m\s*v|m₁v₁\s*\+\s*m₂v₂|'
            r'dp/dt\s*=\s*sum\(F_ext\))',
            re.IGNORECASE,
        )
        self.unit_regex = re.compile(
            r'\b\d+\s*(?:m/s|m/s\^2|N|J|W|Pa|kg|rad/s|kg\.m/s)\b',
            re.IGNORECASE,
        )

    def score(
        self,
        text: str,
        expected_units: Optional[str] = None,
        check_energy: bool = True,
        check_momentum: bool = True,
        check_units: bool = True,
    ) -> float:
        """
        Compute PCS for a single text.

        Args:
            text: Model-generated reasoning/answer.
            expected_units: Expected SI unit string (e.g., 'm/s').
            check_energy: Whether to check for energy marker.
            check_momentum: Whether to check for momentum marker.
            check_units: Whether to check for unit marker.

        Returns:
            PCS ∈ [0, 1].
        """
        active = []
        if check_energy and "energy" in self.markers:
            active.append("energy")
        if check_momentum and "momentum" in self.markers:
            active.append("momentum")
        if check_units and "units" in self.markers:
            active.append("units")

        if not active:
            return 0.0

        points = 0
        if "energy" in active and self.energy_regex.search(text):
            points += 1
        if "momentum" in active and self.momentum_regex.search(text):
            points += 1
        if "units" in active:
            if expected_units and expected_units.lower() in text.lower():
                points += 1
            elif self.unit_regex.search(text):
                points += 1

        return points / len(active)

    def score_batch(self, texts: List[str], expected_units_list: List[Optional[str]]) -> List[float]:
        """Batch scoring."""
        return [
            self.score(t, u) for t, u in zip(texts, expected_units_list)
        ]

    def quality_gate(self, text: str, threshold: float = 0.6, **kwargs) -> bool:
        """Return True if PCS >= threshold."""
        return self.score(text, **kwargs) >= threshold


def cli():
    """Command-line interface for PCS scoring."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Physical Consistency Score (PCS) scorer")
    parser.add_argument("--input", "-i", required=True, help="Input JSON/JSONL of predictions")
    parser.add_argument("--output", "-o", help="Output path for scores")
    parser.add_argument("--threshold", "-t", type=float, default=0.6, help="Quality gate threshold")
    parser.add_argument("--check-energy", action="store_true", default=True)
    parser.add_argument("--check-momentum", action="store_true", default=True)
    parser.add_argument("--check-units", action="store_true", default=True)
    args = parser.parse_args()

    scorer = PCSScorer()

    # Load predictions
    items = []
    with open(args.input, "r", encoding="utf-8") as f:
        if args.input.endswith(".jsonl"):
            for line in f:
                items.append(json.loads(line))
        else:
            items = json.load(f)
            if isinstance(items, dict) and "items" in items:
                items = items["items"]

    results = []
    pass_count = 0
    for item in items:
        text = item.get("prediction", item.get("text", ""))
        expected = item.get("expected_unit")
        pcs = scorer.score(
            text,
            expected_units=expected,
            check_energy=args.check_energy,
            check_momentum=args.check_momentum,
            check_units=args.check_units,
        )
        passed = pcs >= args.threshold
        if passed:
            pass_count += 1
        results.append({
            "id": item.get("id"),
            "pcs": round(pcs, 3),
            "passed_gate": passed,
        })

    summary = {
        "total": len(results),
        "passed": pass_count,
        "pass_rate": round(pass_count / len(results), 3) if results else 0,
        "details": results,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    cli()
