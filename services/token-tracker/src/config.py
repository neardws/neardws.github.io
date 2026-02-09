"""Configuration for token tracker."""
import json
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".openclaw" / "token-tracker.db"
OPENCLAW_BASE = Path.home() / ".openclaw"
DROID_LOG = Path.home() / ".factory" / "logs" / "droid-log-single.log"
RATES_FILE = Path.home() / ".openclaw" / "token-tracker-rates.json"

CLIPROXYAPI_URL = "http://localhost:8317/v0/management/usage"
CLIPROXYAPI_KEY = "tt-admin-2026"

DEFAULT_RATES = {
    "models": {
        "claude-opus-4-5-20251101": {
            "input_per_1m": 15.0,
            "output_per_1m": 75.0,
            "cache_read_per_1m": 1.5,
            "cache_write_per_1m": 18.75
        },
        "claude-sonnet-4-20250514": {
            "input_per_1m": 3.0,
            "output_per_1m": 15.0,
            "cache_read_per_1m": 0.3,
            "cache_write_per_1m": 3.75
        },
        "gpt-5.2": {
            "input_per_1m": 2.5,
            "output_per_1m": 10.0,
            "cache_read_per_1m": 0,
            "cache_write_per_1m": 0
        },
        "kimi-k2-0711": {
            "input_per_1m": 0.55,
            "output_per_1m": 2.19,
            "cache_read_per_1m": 0.14,
            "cache_write_per_1m": 0.55
        },
        "MiniMax-M2.1": {
            "input_per_1m": 1.0,
            "output_per_1m": 4.0,
            "cache_read_per_1m": 0.1,
            "cache_write_per_1m": 0
        }
    },
    "default": {
        "input_per_1m": 3.0,
        "output_per_1m": 15.0,
        "cache_read_per_1m": 0.3,
        "cache_write_per_1m": 3.75
    }
}


def load_rates() -> dict:
    """Load rate configuration from file, falling back to defaults."""
    if RATES_FILE.exists():
        try:
            with open(RATES_FILE) as f:
                user_rates = json.load(f)
            merged = DEFAULT_RATES.copy()
            if "models" in user_rates:
                merged["models"].update(user_rates["models"])
            if "default" in user_rates:
                merged["default"].update(user_rates["default"])
            return merged
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_RATES


def save_rates(rates: dict) -> None:
    """Save rate configuration to file."""
    RATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RATES_FILE, "w") as f:
        json.dump(rates, f, indent=2)


def get_model_rates(model_id: str, rates: Optional[dict] = None) -> dict:
    """Get rates for a specific model."""
    if rates is None:
        rates = load_rates()
    
    if model_id in rates.get("models", {}):
        return rates["models"][model_id]
    
    for key in rates.get("models", {}):
        if key in model_id or model_id in key:
            return rates["models"][key]
    
    return rates.get("default", DEFAULT_RATES["default"])


def calculate_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int,
    cache_write_tokens: int,
    rates: Optional[dict] = None
) -> float:
    """Calculate cost for given token counts."""
    model_rates = get_model_rates(model_id, rates)
    
    cost = 0.0
    cost += (input_tokens / 1_000_000) * model_rates.get("input_per_1m", 0)
    cost += (output_tokens / 1_000_000) * model_rates.get("output_per_1m", 0)
    cost += (cache_read_tokens / 1_000_000) * model_rates.get("cache_read_per_1m", 0)
    cost += (cache_write_tokens / 1_000_000) * model_rates.get("cache_write_per_1m", 0)
    
    return cost
