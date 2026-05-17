# Metrics Documentation

Detailed definitions and implementation notes for all evaluation metrics used in PhysReason-800.

---

## Physical Reasoning Accuracy (PRA)

**Definition**: Fraction of items answered correctly.

### Multiple-Choice Items
- Extract predicted letter (A–E) from model output.
- Correct if exact match with ground-truth answer key.
- Extraction heuristic: first uppercase letter A–E, or regex `([A-E])`.

### Free-Text / Numeric Items
- Extract final numeric answer using cascading regex:
  1. `=\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)` — equation result
  2. `([-+]?\d+\.?\d*)\s*(?:m/s|N|J|rad/s|kg|m|s)` — number with unit
  3. `([-+]?\d+\.?\d*)` — bare number
- Correct if relative error ≤ 5% of ground truth.
- Special case: if GT = 0, absolute error must be < 1e-6.

### Reasoning Quality (LLM-as-Judge)
- On 200 sampled items, GPT-4o rates semantic consistency 1–5.
- Correlation with human raters: r = 0.93.
- Judge prompt explicitly instructs checking numerical correctness, not style.

---

## BERTScore F₁

- Model: `roberta-large` (layer 17)
- Computed between generated explanation and reference explanation.
- Reported at P1 and P9 to measure semantic coherence improvement.

---

## Physical Consistency Score (PCS)

**Range**: [0, 1]

Heuristic over three binary markers (normalized):

| Marker | +1 Condition | Regex Pattern |
|--------|-----------|---------------|
| **Energy** | Mentions conservation of energy or writes energy balance | `(?i)conservation of energy\|KE\s*+\s*PE\|½mv²+mgh` |
| **Momentum** | Mentions conservation of momentum or writes momentum equation | `(?i)conservation of momentum\|p\s*=\s*mv\|dp/dt` |
| **Units** | Final answer includes correct SI unit | `\d+\s*(m/s\|N\|J\|rad/s\|kg·m/s)` |

### Quality Gate
- Recommended threshold: **PCS ≥ 0.6** before deploying LLM-generated physical reasoning.

### Limitations
- **L1**: Cannot verify algebraic correctness symbolically (a model may mention energy balance while making sign errors).
- **L2**: Regex-based; may miss valid but unconventional phrasing.
- **L3**: For GPT-4o outputs, PCS uses GPT-4o-as-judge, creating circular risk (mitigated by human validation, κ = 0.84).

Future work: symbolic execution layer via SymPy.

---

## Conservation Law Violation Rate (CLVR)

**Definition**: Fraction of free-text answers violating at least one analytically verifiable conservation law.

### Detection Heuristic
- For items where ground truth requires energy conservation:
  - Flag violation if output lacks any energy-related mention.
- For items where ground truth requires momentum conservation:
  - Flag violation if output lacks any momentum-related mention.
- **Note**: This is a conservative proxy. True verification requires symbolic parsing of extracted equations.

### Tier-4 (Multi-body) Items
- 100% of Tier-4 items require conservation laws.
- CLVR drops from ~70% (P1) to ~15% (P9) on this subset.

---

## Statistical Tests

### Wilcoxon Signed-Rank Test
- Paired, two-tailed (or one-tailed for directional hypotheses).
- Applied per-model, per-instance PRA scores.
- **Correction**: Holm–Bonferroni across all 36 pairwise prompt comparisons.

### Two-Way Repeated-Measures ANOVA
- Factors: Prompt Level (9) × Model (5)
- Subject: Each of the 800 items (within-item design)
- Sphericity: Mauchly's test; Greenhouse–Geisser correction where violated.
- Reported: partial eta-squared (η²p), F-statistic, p-value.

### Effect Size
- Matched-pairs r = Z / √N
- Interpretation: r > 0.5 large, r > 0.3 medium, r > 0.1 small.

---

## Failure Mode Analysis (P9)

Manual inspection of 80 P9 failures:

| Pattern | Prevalence | Description |
|---------|-----------|-------------|
| Formula hallucination | 36% | Plausible-looking but incorrect equation |
| Unit proliferation | 28% | Unnecessary unit conversions |
| Premature rounding | 21% | Early numerical commitment, propagated error |
| Other | 15% | Off-topic or refusal |

---

## Reproducibility Checklist

- [ ] Temperature = 0.0 for all generations
- [ ] Seed = 42
- [ ] 5 API calls per item (mitigate API-side stochasticity)
- [ ] Max tokens = 1024
- [ ] Exact model versions from `configs/models.yaml`
- [ ] Holm–Bonferroni correction for all pairwise tests
