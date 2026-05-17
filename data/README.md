# PhysReason-800 Dataset

Curated benchmark for physics-informed evaluation of large language models.

## Statistics

| Tier | n | Source | Avg. GT Length (words) | Conservation Laws Required |
|------|---|--------|------------------------|---------------------------|
| T1 – Recall | 200 | SciQ (all) | 18 | 0% |
| T2 – Single-step | 200 | SciQ + PhysicsQA | 41 | 42% |
| T3 – Multi-step | 200 | PhysicsQA + SimVignettes | 87 | 81% |
| T4 – Multi-body | 200 | SimVignettes (all) | 134 | 100% |
| **Total** | **800** | – | **70** | **56%** |

## Splits

| Split | Source | n | Tier | Description |
|-------|--------|---|------|-------------|
| **train** | All three | 640 | All | Stratified 80% |
| **test** | All three | 160 | All | Stratified 20% |
| **tier1_recall** | SciQ only | 200 | Recall | Definition & fact retrieval |
| **tier2_single_step** | SciQ + PhysicsQA | 200 | Single-step | One equation, one unknown |
| **tier3_multi_step** | PhysicsQA + SimVig. | 200 | Multi-step | Sequential reasoning |
| **tier4_multi_body** | SimVignettes only | 200 | Multi-body | Conservation laws required |

## Data Schema

Each item is a JSON object with the following fields:

```json
{
  "id": "T3-Sample-152",
  "tier": "Tier-3",
  "source": "PhysicsQA",
  "question": "A bullet of mass 10g travelling at 400m/s embeds in a stationary block of mass 1kg on a frictionless surface. What is the block's velocity after impact?",
  "ground_truth": {
    "numeric_answer": 3.96,
    "unit": "m/s",
    "explanation": "v = p_i / (m_1 + m_2) = 4 / 1.01 ≈ 3.96 m/s",
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

## Sources & Licensing

### SciQ Subset (312 items)
- **Original**: Welbl et al., EMNLP Workshop 2017
- **License**: CC-BY 4.0
- **Selection criteria**: Topic tags include mechanics, dynamics, fluids, or thermodynamics; require free-text justification

### PhysicsQA Subset (288 items)
- **Original**: Liu et al., arXiv:2311.02512
- **License**: Subject to original authors' terms
- **Selection criteria**: Undergraduate mechanics; stratified over kinematics, Newton's laws, energy, rotational dynamics

### SimVignettes (200 items)
- **Original**: Authored by research team, 2025
- **License**: CC-BY 4.0
- **Description**: Rigid-body and fluid scenarios with analytical ground truth, cross-checked with PyBullet
- **Examples**: Double-pendulum release, coupled rod systems, viscous pipe flow

## Download

The full dataset (`physreason800.json`) and all splits are included in this repository. No external download required.

## Citation

If you use this dataset, please cite the PhysReason-800 paper and the original upstream datasets (see main README).
