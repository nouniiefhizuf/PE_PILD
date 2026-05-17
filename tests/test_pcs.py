"""Unit tests for Physical Consistency Score."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pcs_scorer import PCSScorer


def test_energy_marker():
    scorer = PCSScorer()
    text = "Using conservation of energy: mgh = ½mv²"
    score = scorer.score(text, expected_units="m/s", check_energy=True, check_momentum=False, check_units=True)
    assert score >= 0.5, f"Expected energy marker to fire, got {score}"


def test_momentum_marker():
    scorer = PCSScorer()
    text = "By conservation of momentum: p = mv = constant"
    score = scorer.score(text, expected_units="kg·m/s", check_energy=False, check_momentum=True, check_units=True)
    assert score >= 0.5, f"Expected momentum marker to fire, got {score}"


def test_units_marker():
    scorer = PCSScorer()
    text = "The final velocity is 14.0 m/s"
    score = scorer.score(text, expected_units="m/s", check_energy=False, check_momentum=False, check_units=True)
    assert score == 1.0, f"Expected unit match, got {score}"


def test_no_markers():
    scorer = PCSScorer()
    text = "The answer is 42."
    score = scorer.score(text, expected_units="m/s", check_energy=True, check_momentum=True, check_units=True)
    assert score == 0.0, f"Expected 0.0 for empty text, got {score}"


def test_quality_gate():
    scorer = PCSScorer()
    text = "Energy: KE + PE = constant. Answer: 3.96 m/s"
    assert scorer.quality_gate(text, threshold=0.6, expected_units="m/s")
    assert not scorer.quality_gate(text, threshold=1.0, expected_units="m/s")


def test_batch_scoring():
    scorer = PCSScorer()
    texts = ["v = 5 m/s", "p = mv", "E = mc²"]
    units = ["m/s", "kg·m/s", "J"]
    scores = scorer.score_batch(texts, units)
    assert len(scores) == 3
    assert all(0 <= s <= 1 for s in scores)
