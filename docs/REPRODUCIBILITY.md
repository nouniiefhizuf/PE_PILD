# Reproducibility Guide

Step-by-step instructions to reproduce all paper results.

---

## Environment Setup

### Option A: Conda (Recommended)

```bash
conda env create -f environment.yml
conda activate physreason
pip install -e .
```

### Option B: pip + venv

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scriptsctivate
pip install -r requirements.txt
pip install -e .
```

### API Keys

Create a `.env` file in the repository root:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
TOGETHER_API_KEY=...
```

Or export directly:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export TOGETHER_API_KEY="..."
```

---

## Full Benchmark Reproduction

### Step 1: Run All Model × Prompt Combinations

```bash
python scripts/run_benchmark.py   --models gpt-4o claude-3.5 gemini-1.5 llama-3-70b mixtral-8x22b   --prompt_levels P1 P2 P3 P4 P5 P6 P7 P8 P9   --dataset data/physreason800.json   --output_dir results/raw/   --split test   --n_calls 5   --max_workers 3
```

**Expected runtime**: ~12 hours (depends on API latency and rate limits)
**Estimated cost**: ~$120 USD (varies by provider pricing)
**Carbon footprint**: ≤ 0.34 kg CO₂e (see paper §Ethics)

### Step 2: Compute Statistics

```bash
python scripts/compute_statistics.py   --input_dir results/raw/   --output_dir results/tables/
```

Outputs:
- `wilcoxon_p_{model}.csv` — Pairwise p-value matrices
- `wilcoxon_r_{model}.csv` — Effect size matrices
- `summary_pra.csv` — Mean PRA per model × prompt
- `summary_tier.csv` — Tier-wise breakdown

### Step 3: Generate Figures

```bash
python scripts/generate_figures.py   --results_dir results/raw/   --output_dir results/figures/
```

Outputs:
- `fig2_taxonomy_arrow.{pdf,png}`
- `fig3_tier_curves.{pdf,png}`
- `fig4_model_comparison.{pdf,png}`
- `fig5_heatmap_{model}.{pdf,png}` (one per model)

---

## Partial Reproduction (Quick Check)

Evaluate a single configuration in ~15 minutes:

```bash
python scripts/run_evaluation.py   --model gpt-4o   --prompt_level P7   --split test   --output_dir results/quick/
```

---

## Reproducing ANOVA

The two-way repeated-measures ANOVA requires the full design matrix. Use the notebook:

```bash
jupyter notebook notebooks/03_statistical_analysis.ipynb
```

Or run the Python equivalent (requires `pingouin`):

```python
import pingouin as pg
# See notebook for full code
```

Key parameters:
- Subject: 800 items
- Within-subject factors: Prompt (9 levels), Model (5 levels)
- Sphericity: Mauchly's test → Greenhouse–Geisser if violated

---

## Reproducing PCS

```bash
# Score a single prediction file
python -m src.pcs_scorer   --input results/raw/gpt-4o_P9_test.json   --output results/pcs_gpt4o_p9.json   --threshold 0.6
```

Or programmatically:

```python
from src.pcs_scorer import PCSScorer
scorer = PCSScorer()
score = scorer.score(text, expected_units="m/s")
```

---

## Troubleshooting

### Rate Limits
- Together AI (Llama/Mixtral): 60 requests/minute on free tier
- OpenAI: Tier-1 users may hit TPM limits; reduce `--max_workers` to 1
- Solution: Use `--max_workers 1` and add `time.sleep(1)` between calls if needed

### Determinism
- All experiments use `temperature=0.0` and `seed=42`
- Note: Some providers (e.g., Together AI) do not guarantee bitwise determinism even at T=0
- Mitigation: 5 calls per item, report mean; standard deviation ≤ 0.4 pp in all cells

### Missing API Keys
- The benchmark script will skip models whose API key is missing
- To run only open-weight models: `--models llama-3-70b mixtral-8x22b`

### Memory
- BERTScore requires loading `roberta-large` (~500 MB)
- If OOM, set `device='cpu'` in `src/evaluator.py`

---

## Hardware Used in Original Study

- **API inference**: Cloud-based (OpenAI, Anthropic, Google, Together AI)
- **Local compute**: MacBook Pro M3 (for analysis and figure generation)
- **No GPU required** for reproduction (all models accessed via API)

---

## Version Pinning

All exact versions are recorded in:
- `configs/models.yaml` — Model API versions
- `requirements.txt` / `environment.yml` — Python package versions
- Paper Table 2 — Model version strings

If future API versions produce different outputs, specify the exact version string in your API call.
