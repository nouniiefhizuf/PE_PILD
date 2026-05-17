# Notebook 1: Dataset Exploration

To run: `jupyter notebook notebooks/01_dataset_exploration.ipynb`

## Contents
1. Load PhysReason-800 and inspect tier distribution
2. Visualize question length and complexity
3. Explore conservation law coverage
4. Sample items per tier

## Setup
```python
from src.dataset import PhysReasonDataset
import matplotlib.pyplot as plt

dataset = PhysReasonDataset(split="all", tier="all")
print(dataset.tier_distribution())
```
