from typing import Any, Mapping


def get_attr(obj: Any, key: str) -> Any:
    return obj[key] if isinstance(obj, Mapping) else getattr(obj, key, None)
