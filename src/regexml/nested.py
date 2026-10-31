"""Balanced depth-counter scanner for nested XML tags."""

from __future__ import annotations
import re
from typing import Dict, List, Optional
from regexml.models import TagMatch
from regexml.attributes import parse_attributes, matches_attributes


def find_balanced_tags(
    text: str,
    tag_name: str,
    ignore_case: bool = False,
    match_attributes: Optional[Dict[str, str]] = None,
    allow_unclosed: bool = True,
    match_namespace: bool = False,
) -> List[TagMatch]:
    """
    Find balanced matches for a tag name using a depth counter.
    
    Ensures that when a tag contains nested child tags of the same name:
    <div id="outer">
        <div id="inner">...</div>
    </div>
    the entire outer block is captured from the first opening tag to its corresponding
    balanced closing tag, rather than stopping prematurely at the first closing tag.
    """
    flags = re.DOTALL
    if ignore_case:
        flags |= re.IGNORECASE

    escaped_tag = re.escape(tag_name)
    tag_pattern_str = escaped_tag if match_namespace else rf"(?:[a-zA-Z0-9_.-]+:)?{escaped_tag}"

    # Token regex matches:
    # 1. Opening tag: <tag ...>
    # 2. Closing tag: </tag>
    # 3. Self-closing tag: <tag ... />
    token_re = re.compile(
        rf"(?P<closing></(?P<c_tag>{tag_pattern_str})\s*>)|"
        rf"(?P<self_closing><(?P<s_tag>{tag_pattern_str})(?P<s_attrs>(?:\s+[^>]*?)?)\s*/>)|"
        rf"(?P<opening><(?P<o_tag>{tag_pattern_str})(?P<o_attrs>(?:\s+[^>]*?)?)>)",
        flags,
    )

    matches: List[TagMatch] = []
    text_len = len(text)
    idx = 0

    while idx < text_len:
        # Search for the next token from current idx
        m = token_re.search(text, idx)
        if not m:
            break

        # Check token type
        if m.group("self_closing"):
            # Self-closing tag: completes immediately
            tag_name_found = m.group("s_tag")
            attrs_str = m.group("s_attrs") or ""
            parsed_attrs = parse_attributes(attrs_str)

            if matches_attributes(parsed_attrs, match_attributes):
                match_obj = TagMatch(
                    tag=tag_name_found,
                    content="",
                    attributes=parsed_attrs,
                    raw=m.group(0),
                    start_pos=m.start(),
                    end_pos=m.end(),
                    is_truncated=False,
                )
                matches.append(match_obj)

            idx = m.end()
            continue

        elif m.group("opening"):
            # Opening tag: start tracking balanced depth
            tag_name_found = m.group("o_tag")
            attrs_str = m.group("o_attrs") or ""
            parsed_attrs = parse_attributes(attrs_str)

            # Check if this opening tag satisfies attribute filter
            if not matches_attributes(parsed_attrs, match_attributes):
                idx = m.end()
                continue

            outer_start = m.start()
            content_start = m.end()
            depth = 1
            inner_idx = content_start
            found_closing = False

            while inner_idx < text_len:
                inner_m = token_re.search(text, inner_idx)
                if not inner_m:
                    break

                if inner_m.group("self_closing"):
                    # Self-closing does not alter depth
                    inner_idx = inner_m.end()
                elif inner_m.group("opening"):
                    # Nested opening tag of same name
                    depth += 1
                    inner_idx = inner_m.end()
                elif inner_m.group("closing"):
                    # Closing tag found
                    depth -= 1
                    if depth == 0:
                        # Balanced closing tag reached!
                        content = text[content_start:inner_m.start()]
                        raw = text[outer_start:inner_m.end()]
                        match_obj = TagMatch(
                            tag=tag_name_found,
                            content=content,
                            attributes=parsed_attrs,
                            raw=raw,
                            start_pos=outer_start,
                            end_pos=inner_m.end(),
                            is_truncated=False,
                        )
                        matches.append(match_obj)
                        found_closing = True
                        idx = inner_m.end()
                        break
                    else:
                        inner_idx = inner_m.end()

            if not found_closing:
                # If closing tag was not found and allow_unclosed is enabled (truncated XML)
                if allow_unclosed:
                    content = text[content_start:]
                    raw = text[outer_start:]
                    match_obj = TagMatch(
                        tag=tag_name_found,
                        content=content,
                        attributes=parsed_attrs,
                        raw=raw,
                        start_pos=outer_start,
                        end_pos=text_len,
                        is_truncated=True,
                    )
                    matches.append(match_obj)
                break
        else:
            # Standalone closing tag without opening; skip
            idx = m.end()

    return matches
