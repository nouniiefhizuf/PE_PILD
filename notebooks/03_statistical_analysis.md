# Notebook 3: Statistical Analysis

To run: `jupyter notebook notebooks/03_statistical_analysis.ipynb`

## Contents
1. Two-way repeated-measures ANOVA (Prompt × Model)
2. Polynomial contrasts (linear & quadratic trends)
3. Post-hoc pairwise comparisons with Holm-Bonferroni
4. Effect size computation (matched-pairs r)
5. Mauchly's sphericity test

## Setup
```python
import pingouin as pg
import pandas as pd

# Load long-format data
df = pd.read_csv("results/tables/long_format.csv")

# RM-ANOVA
aov = pg.rm_anova(
    dv='pra',
    within=['prompt_level', 'model'],
    subject='item_id',
    data=df,
    detailed=True
)
print(aov)
```
