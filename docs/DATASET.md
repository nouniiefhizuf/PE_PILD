# Dataset Construction Guide

How PhysReason-800 was built, and how to extend it.

---

## Source Pooling

### S1: SciQ [Welbl et al., 2017]
- **Original size**: 3,000 crowdsourced science questions
- **License**: CC-BY 4.0
- **Filter**: Topic tags ∈ {mechanics, dynamics, fluids, thermodynamics} AND require free-text justification
- **Retained**: 312 items
- **Use in PhysReason**: Tier-1 (all), Tier-2 (partial)

### S2: PhysicsQA [Liu et al., 2023]
- **Original size**: 1,200 expert-authored items
- **License**: Subject to original authors
- **Filter**: Undergraduate mechanics; stratified over 4 sub-domains
  - Kinematics (25%)
  - Newton's laws (25%)
  - Energy/work (25%)
  - Rotational dynamics (25%)
- **Retained**: 288 items
- **Use in PhysReason**: Tier-2 (partial), Tier-3 (partial)

### S3: SimVignettes (Novel)
- **Authored**: Research team, 2025
- **License**: CC-BY 4.0
- **Content**: 200 rigid-body and fluid dynamics scenarios
- **Ground truth**: Computed analytically and cross-checked with **PyBullet** [Coumans & Bai, 2021]
- **Use in PhysReason**: Tier-3 (partial), Tier-4 (all)

---

## Difficulty Tiers

| Tier | n | Cognitive Demand | Conservation Laws | Example |
|------|---|------------------|-------------------|---------|
| **Tier-1** | 200 | Recall / Definition | 0% | "What is Newton's second law?" |
| **Tier-2** | 200 | Single-step algebra | 42% | "Car accelerates 0→27 m/s in 9s; find force" |
| **Tier-3** | 200 | Multi-step reasoning | 81% | "Bullet embeds in block; find final velocity" |
| **Tier-4** | 200 | Multi-body / Lagrangian | 100% | "Coupled rods: find angular velocity" |

### Validation
- 14-respondent expert questionnaire (physics MSc/PhD students)
- Inter-rater agreement: κ = 0.82
- All Tier-4 items confirmed to require explicit conservation law application.

---

## Data Format

```json
{
  "id": "T3-Sample-152",
  "tier": "Tier-3",
  "source": "PhysicsQA",
  "split": "train",
  "question": "...",
  "ground_truth": {
    "numeric_answer": 3.96,
    "unit": "m/s",
    "explanation": "...",
    "equations": ["p = m*v", "v = p_i / (m_1 + m_2)"],
    "conservation_laws": ["conservation_of_momentum"]
  },
  "difficulty": {
    "requires_multi_step": true,
    "requires_conservation_law": true,
    "requires_lagrangian": false
  },
  "metadata": {
    "domain": "mechanics",
    "subdomain": "momentum",
    "simulation_verified": false,
    "pybullet_check": null
  }
}
```

---

## Splits

Stratified random split (seed=42):
- **Train**: 640 items (80%)
- **Test**: 160 items (20%)
- Stratification variables: tier, source, subdomain

Tier-wise files are also provided for targeted evaluation:
- `data/splits/tier1_recall.json`
- `data/splits/tier2_single_step.json`
- `data/splits/tier3_multi_step.json`
- `data/splits/tier4_multi_body.json`

---

## Extending the Dataset

To add new items:

1. Author question and analytical ground truth
2. Verify with symbolic solver (SymPy) or PyBullet
3. Tag with appropriate tier, domain, and conservation laws
4. Run validation script: `python scripts/validate_new_items.py --input new_items.json`
5. Append to `data/physreason800.json` and re-run stratified split generator

### Contribution Guidelines
- Ensure no personally identifiable information
- Maintain CC-BY 4.0 licensing for new SimVignette-style items
- Include complete ground-truth explanation with equations
- Cross-check numerical answers with at least two independent solvers
