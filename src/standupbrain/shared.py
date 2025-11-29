import datetime
import json
from pathlib import Path


def get_config_path() -> Path:
    config_dir = Path.home() / '.config' / 'standupbrain'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'credentials.json'


def get_ollama_model() -> dict | None:
    config_path = get_config_path()
    if not config_path.exists():
        return None

    data = json.loads(config_path.read_text())
    return data.get('ollama_model', 'llama3.2:3b')


def get_previous_workday() -> datetime:
    """Get date of prior workday (weekends considered non workdays)"""
    today = datetime.datetime.now()
    if today.weekday() == 0:
        return today - datetime.timedelta(days=3)
    return today - datetime.timedelta(days=1)
