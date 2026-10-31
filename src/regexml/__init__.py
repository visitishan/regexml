"""regexml: A lightweight, fault-tolerant, text-first XML extraction library for Python."""

from regexml.models import TagMatch, TagReport, XMLText
from regexml.extractor import (
    tagvalue,
    tagvalues,
    tagmatch,
    tagmatches,
    extract_tags,
)
from regexml.inspector import check_tags

__version__ = "0.1.0"
__all__ = [
    "XMLText",
    "TagMatch",
    "TagReport",
    "tagvalue",
    "tagvalues",
    "tagmatch",
    "tagmatches",
    "extract_tags",
    "check_tags",
]
