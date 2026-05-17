"""Evaluation metrics: PRA, BERTScore, CLVR, and LLM-as-judge."""

import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from bert_score import score as bert_score
from scipy.stats import wilcoxon
from statsmodels.stats.multitest import multipletests


class PhysicalReasoningAccuracy:
    """Compute PRA for multiple-choice and free-text items."""

    def __init__(self, numeric_tolerance: float = 0.05):
        self.tolerance = numeric_tolerance

    def score(self, prediction: str, ground_truth: Dict) -> float:
        """
        Returns 1.0 if correct, 0.0 otherwise.
        For MC: exact letter match.
        For numeric: within 5% of ground truth.
        """
        gt = ground_truth

        # Multiple choice
        if "choices" in gt:
            pred_letter = self._extract_mc_choice(prediction)
            return 1.0 if pred_letter == gt.get("answer_letter") else 0.0

        # Numeric extraction
        pred_num = self._extract_number(prediction)
        gt_num = gt.get("numeric_answer")

        if pred_num is None or gt_num is None:
            return 0.0

        if gt_num == 0:
            return 1.0 if abs(pred_num) < 1e-6 else 0.0

        rel_error = abs(pred_num - gt_num) / abs(gt_num)
        return 1.0 if rel_error <= self.tolerance else 0.0

    def _extract_mc_choice(self, text: str) -> Optional[str]:
        text = text.strip().upper()
        if text and text[0] in "ABCDE":
            return text[0]
        match = re.search(r'\b([A-E])\b', text)
        return match.group(1) if match else None

    def _extract_number(self, text: str) -> Optional[float]:
        # Look for patterns like 3.96, 3.96 m/s, = 3.96, etc.
        patterns = [
            r'=\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)',
            r'\b([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*(?:m/s|N|J|rad/s|kg|m|s)\b',
            r'\b([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\b',
        ]
        for pat in patterns:
            matches = re.findall(pat, text)
            if matches:
                try:
                    return float(matches[-1])
                except ValueError:
                    continue
        return None


class BERTScoreMetric:
    """Wrapper for BERTScore F1."""

    def __init__(self, model_type: str = "roberta-large", lang: str = "en"):
        self.model_type = model_type
        self.lang = lang

    def score(self, predictions: List[str], references: List[str]) -> Tuple[float, float, float]:
        """Returns (P, R, F1)."""
        P, R, F1 = bert_score(
            predictions,
            references,
            model_type=self.model_type,
            lang=self.lang,
            verbose=False,
            device="cpu",
        )
        return P.mean().item(), R.mean().item(), F1.mean().item()


class ConservationLawViolationRate:
    """Heuristic detection of conservation law violations in text."""

    def __init__(self):
        self.energy_patterns = [
            r'conservation of energy',
            r'energy is conserved',
            r'KE\s*\+\s*PE',
            r'½\s*mv²\s*\+\s*mgh',
        ]
        self.momentum_patterns = [
            r'conservation of momentum',
            r'momentum is conserved',
            r'p\s*=\s*mv',
            r'm₁v₁\s*\+\s*m₂v₂',
        ]

    def check_violation(self, text: str, ground_truth: Dict) -> bool:
        """
        Returns True if a violation is detected (heuristic).
        Currently checks for absence of required conservation law mentions
        when ground truth requires them.
        """
        required = ground_truth.get("conservation_laws", [])
        text_lower = text.lower()

        if "conservation_of_energy" in required:
            if not any(re.search(p, text_lower) for p in self.energy_patterns):
                # If energy should be conserved but not mentioned, flag as potential violation
                # This is a conservative heuristic
                return True

        if "conservation_of_momentum" in required:
            if not any(re.search(p, text_lower) for p in self.momentum_patterns):
                return True

        return False


class LLMJudge:
    """LLM-as-judge for reasoning quality (semantic consistency)."""

    def __init__(self, judge_model: str = "gpt-4o-2024-11-20"):
        self.judge_model = judge_model
        self.system_prompt = (
            "You are a strict physics grader. Evaluate the following answer for physical correctness, "
            "dimensional consistency, and semantic alignment with the reference. "
            "Respond with a single integer from 1 to 5, where 5 is perfectly correct. "
            "Do not explain your rating."
        )

    def rate(self, prediction: str, reference: str) -> int:
        """Returns integer rating 1-5. Requires API call."""
        # Placeholder: actual implementation would call OpenAI API
        # For reproducibility, we include the judge prompt template
        user_prompt = f"""[Prediction]\n{prediction}\n\n[Reference]\n{reference}\n\nRate (1-5):"""
        # In production, call API here
        return 3  # Stub


class StatisticalTester:
    """Wilcoxon signed-rank and ANOVA helpers."""

    @staticmethod
    def wilcoxon_matrix(scores_matrix: np.ndarray, alternative: str = "greater") -> np.ndarray:
        """
        Compute pairwise Wilcoxon tests.

        Args:
            scores_matrix: shape (n_prompts, n_instances)

        Returns:
            p_matrix: shape (n_prompts, n_prompts), upper-triangle corrected p-values.
        """
        n = scores_matrix.shape[0]
        raw_p = np.ones((n, n))
        pairs = []

        for i in range(n):
            for j in range(i + 1, n):
                try:
                    _, p = wilcoxon(scores_matrix[i], scores_matrix[j], alternative=alternative)
                except ValueError:
                    p = 1.0
                raw_p[i, j] = p
                pairs.append((i, j, p))

        # Holm-Bonferroni correction
        if pairs:
            all_p = [x[2] for x in pairs]
            _, corrected, _, _ = multipletests(all_p, method="holm")
            for k, (i, j, _) in enumerate(pairs):
                raw_p[i, j] = corrected[k]

        return raw_p

    @staticmethod
    def effect_size(r: float) -> str:
        """Cohen's r interpretation."""
        if r > 0.5:
            return "large"
        elif r > 0.3:
            return "medium"
        elif r > 0.1:
            return "small"
        return "negligible"
