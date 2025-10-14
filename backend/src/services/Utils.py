import json
from core.settings import AIConfig


def format_request(prompt: str, context: dict, schema: str = "") -> str:
    return f"{prompt}\n\nContext:\n{json.dumps(context, indent=2)} \n\nSchema:\n{schema}"