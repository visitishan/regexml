"""Data models and XMLText wrapper class for regexml."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class TagMatch:
    """Represents a matched tag with its content, attributes, and location."""
    tag: str
    content: str
    attributes: Dict[str, str] = field(default_factory=dict)
    raw: str = ""
    start_pos: int = -1
    end_pos: int = -1
    is_truncated: bool = False

    def to_xml_text(self) -> XMLText:
        """Convert match content to an XMLText instance carrying metadata."""
        return XMLText(
            self.content,
            is_truncated=self.is_truncated,
            attributes=self.attributes,
            tag=self.tag,
        )


@dataclass
class TagReport:
    """Diagnostic report produced by check_tags()."""
    tags: List[str]
    tag_counts: Dict[str, int]
    unclosed_tags: List[str]
    hierarchy: Dict[str, Any]
    total_tags: int = 0

    def tree(self) -> str:
        """Render a terminal-friendly visual ASCII tree of the tag hierarchy."""
        lines: List[str] = []

        def _render_node(node: Dict[str, Any], prefix: str = ""):
            items = list(node.items())
            for i, (tag_name, children) in enumerate(items):
                is_last = i == len(items) - 1
                connector = "└── " if is_last else "├── "
                unclosed_flag = " (unclosed)" if tag_name in self.unclosed_tags else ""
                lines.append(f"{prefix}{connector}{tag_name}{unclosed_flag}")
                new_prefix = prefix + ("    " if is_last else "│   ")
                if isinstance(children, dict) and children:
                    _render_node(children, new_prefix)

        if not self.hierarchy:
            return "(empty or no tags found)"

        _render_node(self.hierarchy)
        return "\n".join(lines)


_MISSING = object()


class XMLText(str):
    """
    A string subclass that adds resilient XML extraction methods (.tagvalue, .tagvalues, .check_tags).
    
    Acts as a drop-in replacement for standard Python strings with 100% compatibility.
    """

    def __new__(
        cls,
        content: str = "",
        is_truncated: bool = False,
        is_none: bool = False,
        attributes: Optional[Dict[str, str]] = None,
        tag: Optional[str] = None,
    ):
        obj = super().__new__(cls, content)
        obj._is_truncated = is_truncated
        obj._is_none = is_none
        obj._attributes = attributes or {}
        obj._tag = tag
        return obj

    @property
    def is_truncated(self) -> bool:
        """True if the tag content was cut off before its closing tag (e.g., EOF reached)."""
        return self._is_truncated

    @property
    def is_none(self) -> bool:
        """True if this represents an empty/missing tag in a chain."""
        return self._is_none

    @property
    def attributes(self) -> Dict[str, str]:
        """Parsed attributes associated with this tag match."""
        return self._attributes

    @property
    def tag(self) -> Optional[str]:
        """Name of the tag this content was extracted from."""
        return self._tag

    def __bool__(self) -> bool:
        """Evaluate falsy if is_none is True or content is empty."""
        if self._is_none:
            return False
        return len(self) > 0

    def tagvalue(
        self,
        tag_path: str,
        default: Any = _MISSING,
        **kwargs: Any,
    ) -> Any:
        """
        Extract the value of a tag or a nested path of tags (e.g. 'div/name' or 'div.name').
        Supports method chaining: doc.tagvalue('div').tagvalue('name').
        """
        from regexml.extractor import tagvalue as _extract_tagvalue

        # Safe chaining: if this node was already missing in a previous chain call
        if self._is_none:
            if default is not _MISSING:
                return default
            return XMLText("", is_none=True)

        # Handle path notation: e.g. "div/name/first_name" or "div.name.first_name"
        if "/" in tag_path:
            parts = [p.strip() for p in tag_path.split("/") if p.strip()]
        elif "." in tag_path:
            parts = [p.strip() for p in tag_path.split(".") if p.strip()]
        else:
            parts = [tag_path.strip()]

        current: Any = self
        for idx, part in enumerate(parts):
            is_last = idx == len(parts) - 1
            step_default = default if is_last else _MISSING
            
            if hasattr(current, "is_none") and current.is_none:
                if step_default is not _MISSING:
                    return step_default
                return XMLText("", is_none=True)

            current = _extract_tagvalue(str(current), part, default=step_default, **kwargs)
            if current is None or (isinstance(current, XMLText) and current.is_none):
                if is_last and default is not _MISSING:
                    return default
                current = XMLText("", is_none=True)

        if isinstance(current, XMLText) and current.is_none and default is not _MISSING:
            return default

        return current

    def tagvalues(
        self,
        tag: str,
        **kwargs: Any,
    ) -> List[XMLText]:
        """Extract all occurrences of a tag as a list of XMLText objects."""
        from regexml.extractor import tagvalues as _extract_tagvalues

        if self._is_none:
            return []
        return _extract_tagvalues(str(self), tag, **kwargs)

    def check_tags(self, **kwargs: Any) -> TagReport:
        """Inspect all tags, nesting, and unclosed/truncated tags."""
        from regexml.inspector import check_tags as _check_tags

        if self._is_none:
            return TagReport(tags=[], tag_counts={}, unclosed_tags=[], hierarchy={}, total_tags=0)
        return _check_tags(str(self), **kwargs)
