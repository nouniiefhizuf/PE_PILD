"""Unit tests for evaluation metrics."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluator import PhysicalReasoningAccuracy, ConservationLawViolationRate


def test_pra_mc_correct():
    pra = PhysicalReasoningAccuracy()
    gt = {"choices": ["A", "B", "C"], "answer_letter": "B"}
    assert pra.score("The answer is B", gt) == 1.0


def test_pra_mc_incorrect():
    pra = PhysicalReasoningAccuracy()
    gt = {"choices": ["A", "B", "C"], "answer_letter": "B"}
    assert pra.score("The answer is A", gt) == 0.0


def test_pra_numeric_within_tolerance():
    pra = PhysicalReasoningAccuracy(numeric_tolerance=0.05)
    gt = {"numeric_answer": 3.96, "unit": "m/s"}
    assert pra.score("v = 3.95 m/s", gt) == 1.0


def test_pra_numeric_outside_tolerance():
    pra = PhysicalReasoningAccuracy(numeric_tolerance=0.05)
    gt = {"numeric_answer": 3.96, "unit": "m/s"}
    assert pra.score("v = 5.0 m/s", gt) == 0.0


def test_pra_numeric_extraction_equation():
    pra = PhysicalReasoningAccuracy()
    gt = {"numeric_answer": 3600, "unit": "N"}
    assert pra.score("F = m*a = 1200*3 = 3600 N", gt) == 1.0


def test_clvr_energy_violation():
    clvr = ConservationLawViolationRate()
    gt = {"conservation_laws": ["conservation_of_energy"]}
    assert clvr.check_violation("The ball falls down.", gt) is True


def test_clvr_energy_ok():
    clvr = ConservationLawViolationRate()
    gt = {"conservation_laws": ["conservation_of_energy"]}
    assert clvr.check_violation("Using conservation of energy, mgh = ½mv²", gt) is False
