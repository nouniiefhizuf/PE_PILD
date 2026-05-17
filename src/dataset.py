"""PhysReason-800 dataset loader and utilities."""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np


class PhysReasonDataset:
    """Load and filter PhysReason-800 items by split and tier."""

    def __init__(
        self,
        data_path: Optional[str] = None,
        split: str = "test",
        tier: Union[str, List[str]] = "all",
        seed: int = 42,
    ):
        """
        Args:
            data_path: Path to physreason800.json. If None, uses default data/ location.
            split: 'train', 'test', or 'all'.
            tier: 'Tier-1', 'Tier-2', 'Tier-3', 'Tier-4', or 'all'.
            seed: Random seed for shuffling.
        """
        self.split = split
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        if data_path is None:
            # Try default locations
            candidates = [
                Path("data/physreason800.json"),
                Path(__file__).parent.parent / "data" / "physreason800.json",
            ]
            for c in candidates:
                if c.exists():
                    data_path = str(c)
                    break
            if data_path is None:
                raise FileNotFoundError("physreason800.json not found. Please specify data_path.")

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        all_items = data.get("items", [])

        # Filter by split if available in item metadata
        if split != "all":
            all_items = [item for item in all_items if item.get("split", "train") == split]

        # Filter by tier
        if tier != "all":
            if isinstance(tier, str):
                tier = [tier]
            all_items = [item for item in all_items if item.get("tier") in tier]

        self.items = all_items
        self.index_map = {item["id"]: idx for idx, item in enumerate(self.items)}

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> Dict:
        if isinstance(idx, str):
            idx = self.index_map[idx]
        return self.items[idx]

    def get_by_id(self, item_id: str) -> Dict:
        """Retrieve item by its ID (e.g., 'T3-Sample-152')."""
        return self.items[self.index_map[item_id]]

    def filter_by_domain(self, domain: str) -> List[Dict]:
        """Return items matching a domain (e.g., 'mechanics', 'fluids')."""
        return [item for item in self.items if item.get("metadata", {}).get("domain") == domain]

    def filter_by_conservation_law(self, law: str) -> List[Dict]:
        """Return items requiring a specific conservation law."""
        return [
            item for item in self.items
            if law in item.get("ground_truth", {}).get("conservation_laws", [])
        ]

    def sample(self, n: int = 1) -> Union[Dict, List[Dict]]:
        """Randomly sample n items."""
        sampled = self.rng.choice(self.items, size=n, replace=False).tolist()
        return sampled[0] if n == 1 else sampled

    def tier_distribution(self) -> Dict[str, int]:
        """Return count per tier."""
        dist = {}
        for item in self.items:
            t = item.get("tier", "Unknown")
            dist[t] = dist.get(t, 0) + 1
        return dist

    def to_jsonl(self, path: str):
        """Export filtered items to JSONL."""
        with open(path, "w", encoding="utf-8") as f:
            for item in self.items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
