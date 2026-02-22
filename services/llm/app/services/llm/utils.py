import json
from datetime import datetime, date
from pydantic import BaseModel
from app.core.config import LOG_DIR


def get_tool_definition(tool_name: str, model_class: type[BaseModel]) -> dict:
    schema = model_class.model_json_schema()

    schema.pop("title", None)
    for prop in schema.get("properties", {}).values():
        prop.pop("title", None)

    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": (
                model_class.__doc__.strip()
                if model_class.__doc__
                else "No description provided"
            ),
            "parameters": schema,
        },
    }


def json_serial(obj):
    if isinstance(obj, dict):
        return {str(k): json_serial(v) for k, v in obj.items()}

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, (list, tuple, set)):
        return [json_serial(item) for item in obj]

    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    raise TypeError(f"Type {type(obj)} not serializable")


def save_to_json(filename: str, data: dict):
    with open(LOG_DIR / f"{filename}.json", "w") as f:
        json.dump(
            data, f, indent=4, sort_keys=False, ensure_ascii=False, default=json_serial
        )
