"""Core XML extraction engine."""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from regexml.models import _MISSING, TagMatch, XMLText
from regexml.nested import find_balanced_tags
from regexml.utils import remove_comments, strip_all_tags, unwrap_cdata


def tagmatches(
    text: str,
    tag: str,
    ignore_case: bool = False,
    match_attributes: Optional[Dict[str, str]] = None,
    allow_unclosed: bool = True,
    ignore_comments: bool = True,
    match_namespace: bool = False,
    **kwargs: Any,
) -> List[TagMatch]:
    """
    Extract all matching occurrences of a tag as TagMatch objects,
    using balanced depth scanning to accurately capture nested tags.
    """
    if text is None:
        return []

    input_text = str(text)
    if ignore_comments:
        input_text = remove_comments(input_text)

    return find_balanced_tags(
        text=input_text,
        tag_name=tag,
        ignore_case=ignore_case,
        match_attributes=match_attributes,
        allow_unclosed=allow_unclosed,
        match_namespace=match_namespace,
    )


def tagmatch(
    text: str,
    tag: str,
    default: Any = None,
    **kwargs: Any,
) -> Optional[TagMatch]:
    """Extract the first matching TagMatch object for a tag."""
    matches = tagmatches(text, tag, **kwargs)
    return matches[0] if matches else default


def tagvalues(
    text: str,
    tag: str,
    include_tags: bool = False,
    strip_inner_tags: bool = False,
    strip_whitespace: bool = True,
    unwrap_cdata_content: bool = True,
    **kwargs: Any,
) -> List[XMLText]:
    """
    Extract all matching values for a tag name, returned as a list of XMLText instances.
    """
    matches = tagmatches(text, tag, **kwargs)
    results: List[XMLText] = []

    for m in matches:
        content = m.raw if include_tags else m.content

        if unwrap_cdata_content:
            content = unwrap_cdata(content)

        if strip_inner_tags:
            content = strip_all_tags(content)

        if strip_whitespace:
            content = content.strip()

        results.append(
            XMLText(
                content,
                is_truncated=m.is_truncated,
                attributes=m.attributes,
                tag=m.tag,
            )
        )

    return results


def tagvalue(
    text: str,
    tag: str,
    default: Any = _MISSING,
    **kwargs: Any,
) -> Any:
    """
    Extract the value of the first matching tag.
    Returns XMLText instance or default if not found.
    """
    values = tagvalues(text, tag, **kwargs)
    if values:
        return values[0]
    if default is not _MISSING:
        return default
    return XMLText("", is_none=True)


def extract_tags(
    text: str,
    tags: List[str],
    **kwargs: Any,
) -> Dict[str, List[XMLText]]:
    """
    Batch extract multiple distinct tag names from the input text.
    Returns a dictionary mapping tag name to list of XMLText values.
    """
    output: Dict[str, List[XMLText]] = {}
    for t in tags:
        output[t] = tagvalues(text, t, **kwargs)
    return output
