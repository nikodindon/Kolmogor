import json
from pathlib import Path


DEFAULTS = {
    "base_url": "http://localhost:8083/v1",
    "api_key": "sk-placeholder",
    "model": "qwen2.5-coder-7b",
    "context_size": 16384,
    "max_out_tokens": 3000,
    "snapshot_limit": 800,
    "temperature": 0.0,
    "threads": 10,
}


def load_config(path: str = "config.json") -> dict:
    config_path = Path(path)
    if not config_path.exists():
        example = Path("config.example.json")
        if example.exists():
            print(f"[config] config.json not found. Copy config.example.json to config.json and fill in your values.")
        else:
            print(f"[config] config.json not found. Using defaults.")
        return DEFAULTS.copy()

    with open(config_path) as f:
        user_config = json.load(f)

    # Strip comment keys
    user_config = {k: v for k, v in user_config.items() if not k.startswith("_")}

    merged = {**DEFAULTS, **user_config}
    return merged
