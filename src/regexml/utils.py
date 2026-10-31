"""String cleanup and regex helper utilities for regexml."""

from __future__ import annotations
import re

TAG_STRIP_PATTERN = re.compile(r"<[^>]+>", re.DOTALL)
COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)
CDATA_PATTERN = re.compile(r"<!\[CDATA\[(.*?)\]\]>", re.DOTALL)


def strip_all_tags(text: str) -> str:
    """Strip all XML/HTML markup tags from text, leaving only the inner content."""
    if not text:
        return ""
    return TAG_STRIP_PATTERN.sub("", text)


def remove_comments(text: str) -> str:
    """Remove XML comments (<!-- ... -->) from text."""
    if not text:
        return ""
    return COMMENT_PATTERN.sub("", text)


def unwrap_cdata(text: str) -> str:
    """Extract contents of CDATA blocks: <![CDATA[ content ]]> -> content."""
    if not text:
        return ""
    return CDATA_PATTERN.sub(r"\1", text)
