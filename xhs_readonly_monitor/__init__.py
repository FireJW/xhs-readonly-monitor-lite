"""Read-only helpers for inspecting XHS feed state through Chrome DevTools."""

from .state import (
    build_detail_payload,
    extract_detail_from_state,
    extract_feeds_from_state,
    format_posted_at,
)

__all__ = [
    "build_detail_payload",
    "extract_detail_from_state",
    "extract_feeds_from_state",
    "format_posted_at",
]

__version__ = "0.1.0"
