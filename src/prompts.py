"""Prompt template renderer for P1–P9 taxonomy."""

import yaml
from pathlib import Path
from typing import Dict, Optional


class PromptTemplate:
    """Renders one of the nine graded prompt levels."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "prompts.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.prompts = config["prompts"]
        self.validation = config.get("validation", {})

    def render(self, level: str, question: str, example: Optional[str] = None) -> Dict[str, Optional[str]]:
        """
        Render a prompt level.

        Args:
            level: One of P1, P2, ..., P9.
            question: The physics problem text.
            example: Optional one-shot example (used primarily for P9).

        Returns:
            Dict with 'system' and 'user' keys.
        """
        if level not in self.prompts:
            raise ValueError(f"Unknown prompt level: {level}. Choose from {list(self.prompts.keys())}")

        cfg = self.prompts[level]
        system = cfg.get("system")
        user_template = cfg["user_template"]

        # Replace placeholders
        user = user_template.format(question=question)
        if example and "{example}" in user:
            user = user.replace("{example}", example)

        return {
            "name": cfg["name"],
            "phase": cfg["phase"],
            "system": system,
            "user": user,
            "extra_tokens_estimate": cfg.get("extra_tokens_estimate", 0),
        }

    def list_levels(self) -> Dict[str, str]:
        """Return mapping of level ID to human-readable name."""
        return {k: v["name"] for k, v in self.prompts.items()}

    def get_phase(self, level: str) -> str:
        """Return the design phase for a level."""
        return self.prompts[level]["phase"]
