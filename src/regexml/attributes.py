"""Resilient attribute parsing for regexml."""

from __future__ import annotations
import re
from typing import Dict, Optional

# Resilient attribute regex supporting double quotes, single quotes, unquoted values, and boolean flags
ATTR_PATTERN = re.compile(
    r'([a-zA-Z0-9_:-]+)(?:\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+)))?',
    re.MULTILINE,
)


def parse_attributes(attr_string: str) -> Dict[str, str]:
    """
    Parse XML/HTML attributes from a tag's attribute string into a dictionary.
    Handles unquoted values, single quotes, double quotes, and boolean attributes.
    """
    if not attr_string or not attr_string.strip():
        return {}

    attributes: Dict[str, str] = {}
    for match in ATTR_PATTERN.finditer(attr_string):
        name = match.group(1)
        if not name:
            continue
        
        # Determine value among the three quote capture groups
        val_double = match.group(2)
        val_single = match.group(3)
        val_unquoted = match.group(4)

        if val_double is not None:
            value = val_double
        elif val_single is not None:
            value = val_single
        elif val_unquoted is not None:
            value = val_unquoted
        else:
            # Boolean attribute without value (e.g. <input disabled>)
            value = ""

        attributes[name] = value

    return attributes


def matches_attributes(
    parsed_attrs: Dict[str, str],
    filter_attrs: Optional[Dict[str, str]],
) -> bool:
    """Check if all key-value pairs in filter_attrs match the parsed attributes."""
    if not filter_attrs:
        return True

    for k, v in filter_attrs.items():
        if parsed_attrs.get(k) != v:
            return False

    return True
