"""LLM API wrappers with unified interface."""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

import yaml
from pathlib import Path


class BaseModel(ABC):
    """Abstract base for all LLM backends."""

    def __init__(self, config: Dict):
        self.config = config
        self.name = config["name"]
        self.version = config["exact_version"]
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 1024)
        self.seed = config.get("seed", 42)

    @abstractmethod
    def generate(self, system: Optional[str], user: str, n: int = 1) -> List[str]:
        """Generate n responses. Returns list of strings."""
        pass

    def _retry_with_backoff(self, func, max_retries=3):
        """Simple exponential backoff for API calls."""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait = 2 ** attempt
                time.sleep(wait)


class OpenAIModel(BaseModel):
    def __init__(self, config: Dict):
        super().__init__(config)
        import openai
        self.client = openai.OpenAI(api_key=os.getenv(config["api_env_var"]))
        self.model_id = config["exact_version"]

    def generate(self, system: Optional[str], user: str, n: int = 1) -> List[str]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        responses = []
        for _ in range(n):
            resp = self._retry_with_backoff(lambda: self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                seed=self.seed,
            ))
            responses.append(resp.choices[0].message.content)
        return responses


class AnthropicModel(BaseModel):
    def __init__(self, config: Dict):
        super().__init__(config)
        import anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv(config["api_env_var"]))
        self.model_id = config["exact_version"]

    def generate(self, system: Optional[str], user: str, n: int = 1) -> List[str]:
        responses = []
        for _ in range(n):
            resp = self._retry_with_backoff(lambda: self.client.messages.create(
                model=self.model_id,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system or "",
                messages=[{"role": "user", "content": user}],
            ))
            responses.append(resp.content[0].text)
        return responses


class TogetherModel(BaseModel):
    """Wrapper for Together AI (Llama, Mixtral, etc.)."""
    def __init__(self, config: Dict):
        super().__init__(config)
        from together import Together
        self.client = Together(api_key=os.getenv(config["api_env_var"]))
        self.model_id = config["exact_version"]

    def generate(self, system: Optional[str], user: str, n: int = 1) -> List[str]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        responses = []
        for _ in range(n):
            resp = self._retry_with_backoff(lambda: self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            ))
            responses.append(resp.choices[0].message.content)
        return responses


class ModelRegistry:
    """Factory for creating model instances from config."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "configs" / "models.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        self.models = config["models"]
        self.defaults = config.get("defaults", {})

    def get_model(self, model_key: str):
        """Instantiate a model by key (e.g., 'gpt-4o')."""
        if model_key not in self.models:
            raise ValueError(f"Unknown model: {model_key}. Available: {list(self.models.keys())}")
        cfg = self.models[model_key]
        provider = cfg["provider"]

        if provider == "openai":
            return OpenAIModel(cfg)
        elif provider == "anthropic":
            return AnthropicModel(cfg)
        elif provider == "together":
            return TogetherModel(cfg)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def list_models(self) -> Dict[str, str]:
        """Return available models and their types."""
        return {k: f"{v['name']} ({v['type']})" for k, v in self.models.items()}
