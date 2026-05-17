# Convenience commands for PhysReason-800

.PHONY: install test lint figures stats clean

install:
	pip install -e .

test:
	pytest tests/ -v

lint:
	black src/ tests/ scripts/
	flake8 src/ tests/ scripts/

figures:
	python scripts/generate_figures.py --results_dir results/raw/ --output_dir results/figures/

stats:
	python scripts/compute_statistics.py --input_dir results/raw/ --output_dir results/tables/

benchmark:
	python scripts/run_benchmark.py --output_dir results/raw/

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
