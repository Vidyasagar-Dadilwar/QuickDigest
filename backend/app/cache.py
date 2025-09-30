import json
from pathlib import Path
from typing import List, Dict

CACHE_FILE = Path(__file__).resolve().parents[1] / "data" / "articles.json"
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_cache() -> List[Dict]:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding='utf-8'))
        except Exception:
            return []
    return []

def save_cache(items: List[Dict]):
    CACHE_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
