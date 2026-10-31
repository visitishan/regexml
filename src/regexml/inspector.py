"""Tag inspection, hierarchy discovery, and unclosed tag diagnostics."""

from __future__ import annotations
import re
from typing import Any, Dict, List
from regexml.models import TagReport
from regexml.utils import remove_comments

TAG_TOKEN_RE = re.compile(
    r"(?P<closing></(?P<c_tag>[a-zA-Z0-9_.:-]+)\s*>)|"
    r"(?P<self_closing><(?P<s_tag>[a-zA-Z0-9_.:-]+)(?:\s+[^>]*?)?\s*/>)|"
    r"(?P<opening><(?P<o_tag>[a-zA-Z0-9_.:-]+)(?:\s+[^>]*?)?>)",
    re.DOTALL,
)


def check_tags(
    text: str,
    ignore_comments: bool = True,
) -> TagReport:
    """
    Inspect all XML tags within the provided text, building a tag hierarchy
    and identifying any unclosed/truncated tags without validating strict well-formedness.
    """
    if text is None:
        return TagReport(tags=[], tag_counts={}, unclosed_tags=[], hierarchy={}, total_tags=0)

    input_text = str(text)
    if ignore_comments:
        input_text = remove_comments(input_text)

    tag_counts: Dict[str, int] = {}
    stack: List[str] = []
    
    # Hierarchy tree root
    root_hierarchy: Dict[str, Any] = {}
    node_stack: List[Dict[str, Any]] = [root_hierarchy]

    total_tags = 0

    for match in TAG_TOKEN_RE.finditer(input_text):
        if match.group("self_closing"):
            s_tag = match.group("s_tag")
            total_tags += 1
            tag_counts[s_tag] = tag_counts.get(s_tag, 0) + 1
            current_node = node_stack[-1]
            if s_tag not in current_node:
                current_node[s_tag] = {}

        elif match.group("opening"):
            o_tag = match.group("o_tag")
            total_tags += 1
            tag_counts[o_tag] = tag_counts.get(o_tag, 0) + 1
            
            current_node = node_stack[-1]
            if o_tag not in current_node:
                current_node[o_tag] = {}
            
            # Push to stack
            stack.append(o_tag)
            node_stack.append(current_node[o_tag])

        elif match.group("closing"):
            c_tag = match.group("c_tag")
            # If matching opening tag exists on stack
            if c_tag in stack:
                # Pop back up to matching tag to handle missing intermediate tags
                while stack:
                    popped = stack.pop()
                    if len(node_stack) > 1:
                        node_stack.pop()
                    if popped == c_tag:
                        break

    # Any tags remaining on the stack at EOF are unclosed/truncated tags
    unclosed_tags = list(stack)
    tags_list = list(tag_counts.keys())

    return TagReport(
        tags=tags_list,
        tag_counts=tag_counts,
        unclosed_tags=unclosed_tags,
        hierarchy=root_hierarchy,
        total_tags=total_tags,
    )
