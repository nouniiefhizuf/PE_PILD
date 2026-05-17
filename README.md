# PhysReason-800: Physics-Informed Evaluation of LLMs as Simulators

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-2501.xxxxx-b31b1b.svg)](https://arxiv.org)
[![Dataset](https://img.shields.io/badge/Dataset-PhysReason--800-green)](data/)

> **Do Physical Laws Help LLMs Think? Graded Prompt Engineering for Physical Reasoning in Large Language Models**
>
> Ahmed Soltani, Ryan Chanchah, Skander Darghouth, Khalil Ben Rejeb  
> South Mediterranean University (MedTech), Tunis, Tunisia  
> CS321 & Prompt Engineering — Supervisor: Prof. Abdeldjalil Labed

Official implementation of the paper *"Do Physical Laws Help LLMs Think?"*  This repository contains the **PhysReason-800** benchmark, evaluation pipeline, Physical Consistency Score (PCS) scorer, and reproduction scripts for our nine-level graded prompt taxonomy (P1–P9).
---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Results](#key-results)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Dataset](#dataset)
- [Reproduction](#reproduction)
- [Physical Consistency Score (PCS)](#physical-consistency-score-pcs)
- [Citation](#citation)
- [License](#license)

---

## Overview

Large language models (LLMs) excel at pattern recognition but frequently violate physical laws when generating predictions about physical systems—the **Physical Reasoning Gap**. This repository provides:

- **PhysReason-800**: A curated 800-example benchmark across 4 difficulty tiers (Recall → Multi-body)
- **9 Graded Prompt Templates (P1–P9)**: From zero-shot bare to full physics-informed chain-of-thought
- **PCS Scorer**: Automatic verification of conservation law adherence
- **Cross-Model Evaluation**: GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama-3-70B, Mixtral-8x22B

---

## Key Results

| Metric | P1 (Zero-shot) | P9 (Full Physics CoT) | Δ |
|--------|----------------|----------------------|---|
| **PRA (%)** | 57.5 | 84.2 | **+26.7** |
| **BERTScore F₁** | 0.791 | 0.863 | +0.072 |
| **PCS** | 0.311 | 0.748 | +0.437 |
| **CLVR (%)** ↓ | 47.3 | 19.8 | −27.5 |

- **Prompt Level explains 47.1% of variance** (η²p = .471, p < .001)
- **Open-weight models gain more**: Llama-3 & Mixtral improve by +31.1–31.4 pp vs. +22.9–24.1 pp for closed models
- **P7 (Physics CoT) is the efficiency frontier**: Recovers 78% of P9's gain at 45% of token cost

---

## Installation

### From PyPI (coming soon)

```bash
pip install physreason-pcs
```

### From Source

```bash
git clone https://github.com/medtech-tn/physreason-800.git
cd physreason-800
pip install -e .
```

### Environment

```bash
conda env create -f environment.yml
conda activate physreason
```

---

## Quick Start

### 1. Load the Dataset

```python
from src.dataset import PhysReasonDataset

dataset = PhysReasonDataset(split="test", tier="all")
item = dataset[0]
print(item["question"])
# "A 5kg ball is dropped from 10m. What is its speed at impact?"
```

### 2. Evaluate a Single Model

```bash
python scripts/run_evaluation.py \
    --model gpt-4o \
    --prompt_level P7 \
    --split test \
    --output_dir results/
```

### 3. Compute PCS for Generated Outputs

```python
from src.pcs_scorer import PCSScorer

scorer = PCSScorer()
score = scorer.score(
    text="Using conservation of energy: mgh = ½mv² → v = √(2gh) = 14 m/s",
    expected_units="m/s",
    check_energy=True,
    check_momentum=False
)
print(score)  # 0.67
```

### 4. Reproduce All Figures

```bash
python scripts/generate_figures.py --results_dir results/ --output_dir results/figures/
```

---

## Repository Structure

```
physreason-800/
├── configs/               # Model & prompt configurations
│   ├── models.yaml        # API endpoints and model versions
│   └── prompts.yaml       # P1–P9 prompt templates
├── data/                  # PhysReason-800 dataset
│   ├── splits/            # Train/test and tier-wise splits
│   ├── physreason800.json # Full dataset (800 items)
│   └── README.md          # Dataset documentation
├── docs/                  # Extended documentation
│   ├── METRICS.md         # Detailed metric definitions
│   ├── DATASET.md         # Dataset construction guide
│   ├── REPRODUCIBILITY.md # Full reproduction instructions
│   └── PAPER_LINKS.md     # arXiv & supplementary links
├── notebooks/             # Interactive analysis
│   ├── 01_dataset_exploration.ipynb
│   ├── 02_results_reproduction.ipynb
│   └── 03_statistical_analysis.ipynb
├── results/               # Output directory
│   ├── figures/           # Paper figures (PDF/PNG)
│   └── tables/            # LaTeX and CSV result tables
├── scripts/               # Executable scripts
│   ├── run_evaluation.py  # Main evaluation loop
│   ├── run_benchmark.py   # Full P1–P9 × 5-model benchmark
│   ├── generate_figures.py# Figure generation
│   └── compute_statistics.py # ANOVA & Wilcoxon tests
├── src/                   # Source code
│   ├── dataset.py         # Data loading & tier filtering
│   ├── evaluator.py       # PRA, BERTScore, CLVR computation
│   ├── pcs_scorer.py      # Physical Consistency Score
│   ├── models.py          # LLM API wrappers
│   ├── prompts.py         # Prompt template renderer
│   └── utils.py           # Helper utilities
├── tests/                 # Unit tests
│   ├── test_pcs.py
│   └── test_evaluator.py
├── CITATION.cff           # Citation metadata
├── LICENSE                # MIT License
├── README.md              # This file
├── environment.yml        # Conda environment
├── requirements.txt       # Python dependencies
└── setup.py               # Package installer
```

---

## Dataset

### PhysReason-800 Splits

| Split | Source | n | Tier | Description |
|-------|--------|---|------|-------------|
| **Train** | All three | 640 | All | Stratified 80% |
| **Test** | All three | 160 | All | Stratified 20% |
| **Tier-1** | SciQ only | 200 | Recall | Definition & fact retrieval |
| **Tier-2** | SciQ + PhysicsQA | 200 | Single-step | One equation, one unknown |
| **Tier-3** | PhysicsQA + SimVig. | 200 | Multi-step | Sequential reasoning |
| **Tier-4** | SimVignettes only | 200 | Multi-body | Conservation laws required |

### Sources
- **SciQ** [Welbl et al., 2017]: 312 mechanics/dynamics/fluids/thermodynamics items (CC-BY 4.0)
- **PhysicsQA** [Liu et al., 2023]: 288 undergraduate mechanics items
- **SimVignettes**: 200 novel rigid-body/fluid scenarios with analytical ground truth (cross-checked with PyBullet)

Load specific tiers:
```python
from src.dataset import PhysReasonDataset
tier4 = PhysReasonDataset(split="test", tier="Tier-4")
```

See [docs/DATASET.md](docs/DATASET.md) for full schema and construction details.

---

## Reproduction

### Full Paper Reproduction (P1–P9 × 5 Models)

```bash
# 1. Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TOGETHER_API_KEY="..."

# 2. Run full benchmark (~2 GPU-hours equivalent, ~0.34 kg CO₂e)
python scripts/run_benchmark.py \
    --models gpt-4o claude-3.5 gemini-1.5 llama-3-70b mixtral-8x22b \
    --prompt_levels P1 P2 P3 P4 P5 P6 P7 P8 P9 \
    --dataset data/physreason800.json \
    --output_dir results/raw/ \
    --temperature 0.0 \
    --seed 42 \
    --n_calls 5

# 3. Compute statistics (ANOVA, Wilcoxon, effect sizes)
python scripts/compute_statistics.py \
    --input_dir results/raw/ \
    --output_dir results/tables/

# 4. Generate all figures
python scripts/generate_figures.py \
    --results_dir results/raw/ \
    --output_dir results/figures/
```

### Expected Runtime
- Single model × single prompt level: ~15 min (800 items, 5 calls each)
- Full benchmark (5 models × 9 levels): ~12 hours
- Statistical analysis + figures: ~5 minutes

See [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) for per-model API details, cost estimates, and troubleshooting.

---

## Physical Consistency Score (PCS)

PCS is a lightweight heuristic that verifies whether generated reasoning respects conservation laws. It checks three binary markers:

1. **Energy balance equation present** (+1)
2. **Momentum conservation stated or used** (+1)
3. **Final answer has correct units** (+1)

PCS ∈ [0, 1], normalized over active markers. Inter-annotator agreement: κ = 0.84.

```bash
# Install standalone scorer
pip install physreason-pcs

# Use as quality gate
python -m physreason_pcs --input predictions.json --threshold 0.6
```

See [docs/METRICS.md](docs/METRICS.md) for full specification and failure-mode analysis.

---

## Citation

If you use PhysReason-800, the PCS scorer, or the P1–P9 taxonomy in your research, please cite:

```bibtex
@inproceedings{soltani2025physical,
  title={Do Physical Laws Help LLMs Think? Graded Prompt Engineering for Physical Reasoning in Large Language Models},
  author={Soltani, Ahmed and Chanchah, Ryan and Darghouth, Skander and Ben Rejeb, Khalil},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2025},
  organization={South Mediterranean University (MedTech)},
  url={https://github.com/medtech-tn/physreason-800}
}
```

Also consider citing the upstream datasets:
```bibtex
@inproceedings{welbl2017crowdsourcing,
  title={Crowdsourcing Multiple Choice Science Questions},
  author={Welbl, Johannes and Liu, Nelson F and Gardner, Matt},
  booktitle={EMNLP Workshop on Teaching NLP},
  year={2017}
}

@article{liu2023physicsbench,
  title={PhysicsBench: Benchmarking and Enhancing Vision-Language Models for Physical World Understanding},
  author={Liu, Jingyuan and Yin, Wenhao and Yu, Zhenyu and Zhang, Yue and Wan, Yudong and Sun, Lichao},
  journal={arXiv preprint arXiv:2311.02512},
  year={2023}
}
```

---

## License

- **Code & SimVignettes**: MIT License (see [LICENSE](LICENSE))
- **PhysReason-800 dataset**: CC-BY 4.0
- **SciQ subset**: CC-BY 4.0 (original license)
- **PhysicsQA subset**: Subject to original authors' terms

---

## Acknowledgements

We thank Prof. Abdeldjalil Labed for guidance throughout the project and the 14 expert validators who completed our questionnaire. Ahmed Soltani and Skander Darghouth contributed to prompt design and statistical analysis; Ryan Chanchah led dataset curation; Khalil Ben Rejeb implemented the evaluation pipeline.

**Contact**: {ahmed.soltani, ryan.chanchah, skanderjalel.darghouth, khalil.benrejeb}@medtech.tn

---

<div align="center">
  <sub>Built with ❤️ at South Mediterranean University (MedTech), Tunis</sub>
</div>
