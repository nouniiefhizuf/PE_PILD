"""Utility functions for logging, caching, and data I/O."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict

import yaml


def get_project_root() -> Path:
    """Return repository root."""
    return Path(__file__).parent.parent


def load_yaml(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_jsonl(data: list, path: str):
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def load_jsonl(path: str) -> list:
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def cache_key(*args) -> str:
    """Deterministic cache key from arguments."""
    content = json.dumps(args, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)


def format_ci(p: float, n: int, z: float = 1.96) -> str:
    """Wilson score interval for proportion."""
    from math import sqrt
    denominator = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denominator
    margin = z * sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator
    return f"[{centre - margin:.3f}, {centre + margin:.3f}]"
