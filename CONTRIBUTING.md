# Contributing to PhysReason-800

We welcome contributions that improve reproducibility, extend the benchmark, or add new models.

## How to Contribute

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature`
3. **Commit** your changes with clear messages
4. **Push** to your fork
5. **Open a Pull Request** against `main`

## Contribution Types

### 🐛 Bug Fixes
- Include a minimal reproduction case
- Add a test in `tests/` that would have failed before the fix

### 📊 New Models
- Add model config to `configs/models.yaml`
- Implement provider wrapper in `src/models.py` if needed
- Run evaluation on at least Tier-2 and Tier-4 items
- Report mean PRA and PCS in PR description

### 🧪 New Prompt Levels
- Follow the P1–P9 design principle: **one new physics-grounding element per level**
- Validate with at least 5 physics graduate students (Likert 1–7)
- Include token overhead estimate
- Document in `configs/prompts.yaml` and `docs/METRICS.md`

### 📖 Dataset Items
- See `docs/DATASET.md` for extension guidelines
- Ensure analytical ground truth is verified with SymPy or PyBullet
- Tag with correct tier, domain, and conservation laws

## Code Style

- **Python**: Black formatter (`black src/ tests/ scripts/`)
- **Imports**: isort-compatible
- **Types**: Use type hints for public functions
- **Docstrings**: Google-style

## Testing

```bash
pytest tests/ -v
```

All PRs must pass existing tests and include new tests for added functionality.

## Commit Message Format

```
type(scope): subject

body

footer
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(pcs): add symbolic verification layer

Implements SymPy-based equation parsing to detect sign errors
in energy balance equations. Closes #12.
```

## Code of Conduct

- Be respectful and constructive
- Prioritize scientific rigor over speed
- Acknowledge original dataset authors when extending data

## Questions?

Open a [GitHub Discussion](https://github.com/medtech-tn/physreason-800/discussions) or email the authors.
