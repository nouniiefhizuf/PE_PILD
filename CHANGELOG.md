# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] — 2025-05-17

### Added
- Initial release of PhysReason-800 benchmark (800 items, 4 tiers)
- Nine-level graded prompt taxonomy (P1–P9) with validation
- PCS (Physical Consistency Score) scorer v1.0
- Evaluation pipeline for 5 LLMs (GPT-4o, Claude 3.5, Gemini 1.5, Llama-3-70B, Mixtral-8x22B)
- Full reproduction scripts for NeurIPS 2025 paper
- Statistical analysis suite (Wilcoxon, ANOVA, effect sizes)
- Figure generation scripts (Figures 2–5)
- Comprehensive documentation (METRICS, DATASET, REPRODUCIBILITY)

### Known Issues
- PCS is regex-based and cannot verify symbolic correctness (see docs/METRICS.md)
- Together AI backend may show minor non-determinism even at T=0.0
- BERTScore requires ~500 MB model download on first run

## [0.9.0] — 2025-04-20

### Added
- Beta benchmark with 600 items
- Internal validation questionnaire (n=14)
- PyBullet cross-check for SimVignettes

### Changed
- Expanded from 5 to 9 prompt levels after pilot study

## [0.5.0] — 2025-03-10

### Added
- Initial SimVignettes (50 items)
- Pilot evaluation on GPT-4o and Llama-3-70B
