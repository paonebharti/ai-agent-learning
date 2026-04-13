import json
import os


class PromptServiceError(Exception):
    pass


class PromptService:
    def __init__(self, prompts_path: str = "prompts.json"):
        self.prompts_path = prompts_path
        self._data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.prompts_path):
            raise PromptServiceError(f"Prompts file not found: {self.prompts_path}")
        with open(self.prompts_path, "r") as f:
            self._data = json.load(f)
        print(f"📝 Loaded {len(self._data['variants'])} prompt variants. Active: {self._data['active_variant']}")

    def _save(self):
        with open(self.prompts_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_active(self) -> dict:
        active_key = self._data["active_variant"]
        variant = self._data["variants"].get(active_key)
        if not variant:
            raise PromptServiceError(f"Active variant '{active_key}' not found")
        return {
            "key": active_key,
            **variant
        }

    def get_variant(self, key: str) -> dict:
        variant = self._data["variants"].get(key)
        if not variant:
            raise PromptServiceError(f"Variant '{key}' not found")
        return {"key": key, **variant}

    def set_active(self, key: str):
        if key not in self._data["variants"]:
            raise PromptServiceError(f"Variant '{key}' not found")
        self._data["active_variant"] = key
        self._save()
        print(f"📝 Active prompt switched to: {key}")

    def list_variants(self) -> dict:
        return {
            "active": self._data["active_variant"],
            "variants": {
                k: {"name": v["name"]}
                for k, v in self._data["variants"].items()
            }
        }

    def add_variant(self, key: str, name: str, system_prompt: str,
                    temperature: float = 0.2, max_tokens: int = 200):
        if key in self._data["variants"]:
            raise PromptServiceError(f"Variant '{key}' already exists")
        self._data["variants"][key] = {
            "name": name,
            "system_prompt": system_prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        self._save()
        print(f"📝 Added new prompt variant: {key}")
