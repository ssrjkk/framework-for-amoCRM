import json
import os
from config.settings import LOAD_THRESHOLDS

THRESHOLDS = LOAD_THRESHOLDS

BASELINE_FILE = "reports/load/baseline.json"


def load_baseline():
    if os.path.exists(BASELINE_FILE):
        with open(BASELINE_FILE, "r") as f:
            return json.load(f)
    return None


def save_baseline(stats: dict):
    os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)
    with open(BASELINE_FILE, "w") as f:
        json.dump(stats, f, indent=2)


def get_baseline():
    return load_baseline()


def compare_with_baseline(current: dict, baseline: dict) -> dict:
    if not baseline:
        return {"status": "no_baseline", "changes": {}}
    
    changes = {}
    for key in ["avg_response_time", "p95_response_time", "rps", "error_rate"]:
        if key in current and key in baseline:
            curr_val = current[key]
            base_val = baseline[key]
            if base_val:
                pct_change = ((curr_val - base_val) / base_val) * 100
                changes[key] = {
                    "current": curr_val,
                    "baseline": base_val,
                    "change_pct": round(pct_change, 2),
                    "regression": pct_change > 10
                }
    
    regressed = any(c.get("regression", False) for c in changes.values())
    return {"status": "regression" if regressed else "ok", "changes": changes}


BASELINE = get_baseline()