import mimetypes
from typing import Dict, Set

from app.config import settings


def build_extension_to_mime(allowed_extensions: Set[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for ext in allowed_extensions:
        mime_type, _ = mimetypes.guess_type(f"file{ext}")
        if mime_type:
            mapping[ext] = mime_type
    return mapping


EXTENSION_TO_MIME = build_extension_to_mime(settings.allowed_extensions_set)
