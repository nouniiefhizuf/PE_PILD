# Notebook 2: Results Reproduction

To run: `jupyter notebook notebooks/02_results_reproduction.ipynb`

## Contents
1. Load raw result JSONs
2. Reproduce Table 3 (Main Accuracy Results)
3. Reproduce Table 4 (Metric Comparison P1 vs P9)
4. Reproduce Figure 3 (Tier curves)
5. Reproduce Figure 4 (Model comparison)

## Setup
```python
import pandas as pd
from scripts.generate_figures import load_results

df = load_results("results/raw/")
summary = df.groupby(["model", "prompt_level"])["pra"].mean().unstack()
print(summary)
```
