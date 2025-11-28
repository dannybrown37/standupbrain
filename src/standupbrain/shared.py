import datetime

OLLAMA_MODEL = 'qwen2.5:3b'


def get_previous_workday() -> datetime:
    """Get date of prior workday (weekends considered non workdays)"""
    today = datetime.datetime.now()
    if today.weekday() == 0:
        return today - datetime.timedelta(days=3)
    return today - datetime.timedelta(days=1)
