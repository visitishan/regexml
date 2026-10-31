# Technical Specification Document: `regexml` (Resilient Text-Based XML Extractor)

- **Document Version:** 1.0.0
- **Status:** Approved / Draft
- **Author:** Ishan & Antigravity
- **Target Language:** Python 3.9+
- **Created Date:** 2026-10-31

---

## 1. Executive Summary & Motivation

Traditional XML parsing libraries in Python (such as `xml.etree.ElementTree`, `lxml`, `minidom`, `xmltodict`) operate by strictly validating XML syntax, building an In-Memory Document Object Model (DOM) tree, and navigating nodes.

### The Problem
In real-world applications, strict XML parsers often fail drastically:
1. **Malformed or Incomplete XML:** A single missing closing tag, unescaped ampersand (`&`), or unquoted attribute causes `XMLSyntaxError` / `ParseError`, crashing the entire parsing process even if the desired tag's data is completely intact.
2. **LLM Output Parsing:** Large Language Models (LLMs) frequently wrap responses in pseudo-XML tags (e.g., `<thought>...</thought>`, `<answer>...</answer>`) which might contain raw markdown, code snippets, unescaped brackets, or truncated text.
3. **Log & Stream Scraping:** Server logs or network packet dumps often contain isolated XML snippets mixed with plain text where a complete root document does not exist.
4. **Performance Overhead:** Parsing huge multi-gigabyte XML files into a DOM tree consumes significant memory and CPU cycles when all the user needs is a few specific tags (e.g., `<OrderNumber>` or `<Status>`).

### The Solution: `regexml`
`regexml` is a lightweight, fault-tolerant, text-first XML extraction library for Python. It treats XML purely as plain text, using optimized Regular Expressions and pattern scanning to extract tag contents directly. It never validates document hierarchy or schema, allowing users to reliably pull tag values out of broken, truncated, or dirty XML.

---

## 2. Core Design Principles

1. **Zero Schema / Tree Enforcement:** No root element required, no validation of well-formedness. If a tag pair exists in the text, its content can be extracted.
2. **Graceful Fault Tolerance:** Never throw fatal syntax exceptions on malformed surroundings. If `<target>data</target>` is valid, it will be found even if the rest of the file is broken.
3. **Ergonomic & Intuitive API:** Simple, Pythonic functions like `extract_tag(text, "tag")` and `extract_all(text, "tag")` with no boilerplate.
4. **Zero Heavy Dependencies:** Built on Python's standard library (`re`, `typing`, `dataclasses`) with optional zero-dependency lightweight helpers.
5. **Flexible Output Formatting:** Support for raw inner content, stripped text, tag attributes extraction, and dict mapping.

---

## 3. Scope & Target Use Cases

| Use Case | Why Traditional Parsers Fail | How `regexml` Solves It |
|---|---|---|
| **LLM Output Extraction** | LLM outputs contain unescaped `<`, `>`, `&`, or unclosed markdown inside XML tags | Matches specific `<tag>...</tag>` patterns regardless of unescaped inner content |
| **Truncated / Partial XML** | Network timeout or buffer limit cuts off closing tags at the document end | Extracts all fully closed tags that made it through before truncation |
| **Dirty Log Files** | Log files contain XML mixed with timestamp headers, stack traces, and noise | Direct regex scan ignores surrounding non-XML text |
| **Quick Key-Value Extraction** | Loading large DOM trees to read 2 fields is slow and memory-intensive | Regex stream scan quickly extracts targets without DOM overhead |

---

## 4. API Design & Specification

### 4.1. Two Ways to Use: String Wrapper (Fluent Dot-Syntax) & Functional API

To provide the developer ergonomics requested (`my_text_data.tagvalue("div")`), `regexml` provides two complementary usage patterns:

#### A. Fluent Dot-Syntax via `XMLText` (`str` Subclass)
In Python, built-in `str` cannot be directly patched with new methods. However, by subclassing Python's native `str` in `class XMLText(str)`, user data behaves **100% like a normal string** (supports slicing, `.strip()`, `len()`, string formatting, passing to any standard library function) while unlocking direct `.tagvalue()` dot-methods:

```python
from regexml import XMLText

# User wraps or instantiates text with XMLText
my_text_data = XMLText("""
<article>
    <div class="main">
        Outer content
        <div class="sub">Inner content</div>
        Closing note
    </div>
</article>
""")

# Fluent dot-syntax:
extracted_value = my_text_data.tagvalue("div")
# Returns: 'Outer content\n        <div class="sub">Inner content</div>\n        Closing note'

# Or multiple values:
all_divs = my_text_data.tagvalues("div")

# Or dynamic attribute access:
title = my_text_data.tagvalue("title", default="Untitled")
```

#### Method Chaining & Path-Based Drill-Down
Because `tagvalue()` returns an `XMLText` instance (which is both a valid `str` and has `.tagvalue()` methods), users can naturally chain multiple `.tagvalue()` calls to drill down into nested structures:

```python
# 1. Fluent Method Chaining:
first_name = my_text_data.tagvalue("div").tagvalue("name").tagvalue("first_name")

# 2. Path Syntax Shorthand:
first_name = my_text_data.tagvalue("div/name/first_name")
# or:
first_name = my_text_data.tagvalue("div.name.first_name")
```

##### Safe Chaining (No `AttributeError` crashes):
If an intermediate tag is missing (e.g. `<name>` doesn't exist), standard chaining would fail if `None` was returned. To prevent crashes, `XMLText` returns a `SafeXMLText` (or empty `XMLText` with `is_none=True` / falsy value) that safely chains calls, returning `default` (or `None`/`""`) at the end of the chain without raising `AttributeError`!

```python
# Even if <non_existent> is missing, does NOT raise AttributeError:
result = my_text_data.tagvalue("div").tagvalue("non_existent").tagvalue("first_name", default="N/A")
# Returns: "N/A"
```

#### B. Direct Functional API
For users who do not wish to wrap their string:
```python
from regexml import tagvalue, tagvalues

extracted_value = tagvalue(my_raw_str, "div")
all_values = tagvalues(my_raw_str, "div")
```

---

### 4.2. Core Method & Function Signatures

#### `tagvalue(tag: str, default: Any = None, **kwargs) -> Optional[str]`
- On `XMLText`: `my_text_data.tagvalue(tag, default=None, **kwargs)`
- Functional: `tagvalue(text, tag, default=None, **kwargs)`
- Extracts the value of the first matching tag. Handles balanced nesting automatically so outer tags are not prematurely cut off. Returns `default` if tag is not found.

#### `tagvalues(tag: str, **kwargs) -> List[str]`
- On `XMLText`: `my_text_data.tagvalues(tag, **kwargs)`
- Functional: `tagvalues(text, tag, **kwargs)`
- Extracts all balanced occurrences of the specified tag name.

#### `extract_tags(tags: List[str], **kwargs) -> Dict[str, List[str]]`
- Extracts multiple distinct tag names in a single scan.

#### `tagmatch(tag: str, **kwargs) -> Optional[TagMatch]` / `tagmatches(tag: str, **kwargs) -> List[TagMatch]`
- Returns `TagMatch` objects containing both tag content and parsed attribute key-value pairs.

#### `check_tags(**kwargs) -> TagReport` (Tag Inspection & Hierarchy Discovery)
- On `XMLText`: `report = my_text_data.check_tags()`
- Functional: `report = check_tags(text)`
- Scans the text and returns a comprehensive `TagReport` containing:
  - `tags`: List of all unique tags found.
  - `tag_counts`: Frequency count of each tag.
  - `unclosed_tags`: List of tags opened but never closed (critical for pinpointing truncation!).
  - `hierarchy`: Nested dictionary structure of parent-child tag relationships.
  - `report.tree()`: Generates a terminal-friendly visual ASCII tree diagram (e.g. `catalog └── item └── price`).

---

### 4.3. Configuration Parameters (`**kwargs`)

| Parameter | Type | Default | Description |
|---|---|---|---|
| `include_tags` | `bool` | `False` | If `True`, returns `<tag>content</tag>`. If `False`, returns only inner `content`. |
| `strip_inner_tags` | `bool` | `False` | If `True`, removes any inner markup (e.g. `<b>bold</b>` becomes `bold`). |
| `strip_whitespace` | `bool` | `True` | If `True`, strips leading/trailing whitespace from returned values. |
| `ignore_case` | `bool` | `False` | If `True`, matches `<div` and `</DIV>` case-insensitively. |
| `multiline` | `bool` | `True` | If `True`, matches content across multiple lines (`re.DOTALL`). |
| `match_attributes` | `Optional[Dict[str, str]]` | `None` | Filter tags that have specific attribute values (e.g. `{'class': 'main'}`). |
| `handle_nested` | `bool` | `True` | Default `True`. Uses balanced depth-counter to ensure outermost opening tag matches its true closing tag. |
| `allow_unclosed` | `bool` | `True` | If `True`, if a closing tag is missing (e.g. truncated XML cutoff at EOF), extracts content up to EOF or next peer tag instead of failing. |

---

### 4.4. Data Structures

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class TagMatch:
    tag: str
    content: str
    attributes: Dict[str, str] = field(default_factory=dict)
    raw: str = ""
    start_pos: int = -1
    end_pos: int = -1
    is_truncated: bool = False  # True if closing tag was missing and captured up to EOF

@dataclass
class TagReport:
    tags: List[str]
    tag_counts: Dict[str, int]
    unclosed_tags: List[str]
    hierarchy: Dict[str, Any]
    total_tags: int = 0

    def tree(self) -> str:
        """Returns a formatted visual ASCII tree representation of the tag hierarchy."""
        ...
```

---

## 5. Technical Architecture & Algorithm Design

### 5.1. Regular Expression Strategy

#### Base Tag Matching Pattern:
```regex
<(?P<tag>{tag_name})(?P<attrs>(?:\s+[^>]*?)?)>(?P<content>.*?)</(?P=tag)>
```
- **Flag:** `re.DOTALL` (multiline matching).
- **Non-Greedy Match (`.*?`):** Ensures we match the closest closing tag rather than swallowing multiple sibling tags.
- **Attributes Capture:** Allows extracting `<tag id="123" class="data">` cleanly while preserving tag matching.

#### Handling Self-Closing Tags:
```regex
<(?P<tag>{tag_name})(?P<attrs>(?:\s+[^>]*?)?)\s*/>
```
For self-closing tags, content is considered empty `""` or `None`, while attributes are captured.

### 5.2. Handling Nested Tags of the Same Name (Balanced Outermost Scanner)

A major flaw in naive regex solutions is the **premature closing tag bug**:
```xml
<div id="outer">
    Outer Content Before
    <div id="inner">
        Nested Content
    </div>
    Outer Content After
</div>
```
A standard non-greedy regex `<div>(.*?)</div>` stops at the *first* closing tag (`</div>` from `inner`), completely chopping off `Outer Content After</div>` and corrupting the output.

#### Our Balanced Depth Algorithm:
To guarantee that the user gets the **full block from the first opening tag to its corresponding balanced closing tag**:
1. Scan for occurrences of `<tag(\s+[^>]*)?>` (opening) and `</tag>` (closing).
2. When the first opening tag is hit at index $S$, record its inner content start position and initialize `depth = 1`.
3. As the scanner moves forward:
   - If another `<tag>` of the same name is found: `depth += 1`
   - If `</tag>` is found: `depth -= 1`
4. The moment `depth == 0`, we have reached the **true matching closing tag** for that outermost opening tag.
5. Slice the string directly between opening tag end and closing tag start.
6. This runs in $O(N)$ linear time without parsing the document tree, and correctly captures the entire nested body.
7. If the XML is truncated (e.g. `depth` never reaches 0 due to network cutoff), the engine gracefully falls back to returning all content up to the end of text or up to the last known closing tag without raising an exception.

### 5.3. Attribute Parsing Strategy
Attributes are parsed using a resilient regex:
```regex
([a-zA-Z0-9_:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))
```
This handles double quotes, single quotes, and unquoted values (common in malformed XML/HTML).

### 5.4. Truncated XML Recovery & Tag Inspection Algorithm

#### 1. Graceful Truncation Recovery (`allow_unclosed=True`)
When XML is abruptly cut off (e.g. only 1000 lines saved out of 1200):
- If the requested tag has its closing tag earlier in the document, it extracts normally.
- If the requested tag opened at or near the cutoff point (e.g. `<item>` opened at line 980 and file ends at line 1000 without `</item>`):
  1. The scanner checks if `allow_unclosed=True` (default).
  2. If a closing tag is not found, the scanner extracts from the end of the opening `<tag...>` all the way to **End-Of-File (EOF)** or the start of a new sibling tag.
  3. The extracted `XMLText` or `TagMatch` marks `is_truncated = True`.
  4. The user receives all available partial data rather than an empty string or crash.

#### 2. Tag Inspection & Hierarchy Discovery (`check_tags()`)
To map out tags and detect broken/unclosed markup without a strict XML parser:
- Uses a fast regex stream tokenizer matching all `<tag ...>` and `</tag>` tokens.
- Maintains a lightweight tag tracking stack:
  - On opening tag: Push `tag` onto stack; record occurrences.
  - On closing tag `</tag>`: Check stack. If matching tag is on stack, pop it and record it as `closed`.
  - Self-closing tags (`<tag />`): Recorded directly as self-contained.
- **Diagnostics produced:**
  - **`unclosed_tags`:** Any tags still left in the stack at EOF are unclosed/truncated tags (e.g. `['root', 'catalog', 'item']`), immediately revealing where and why the XML was truncated!
  - **`hierarchy`:** As tokens are pushed/popped, parent-child relationships are registered in a tree dictionary.
  - **`tree()`:** Prints a clean ASCII tree representation.

---

## 6. Edge Cases & Resilience Strategy

1. **Unescaped Special Characters (`<`, `>`, `&` in data):**
   - Traditional parsers fail when raw `<` appears in text.
   - `regexml` relies on boundary lookaheads and the specific closing tag `</tag_name>`.
2. **Missing Closing Tag for Outer Wrapper:**
   - Inner target tags will still be extracted cleanly without error.
3. **CD-DATA Blocks (`<![CDATA[ ... ]]>`):**
   - CDATA contents are preserved or transparently unwrapped based on configuration.
4. **XML Comments (`<!-- ... -->`):**
   - Option `ignore_comments: bool = True` to strip comments before searching so commented-out tags are not extracted.
5. **Namespaced Tags (`<ns:Item>...</ns:Item>`):**
   - Supports namespace-aware extraction (`tag="ns:Item"`) or namespace-agnostic extraction (`tag="Item"`, matching any `prefix:Item`).

---

## 7. Project Structure & Packaging

```text
XML library/
├── SPECIFICATION.md          # This technical specification
├── PROGRESS.md               # Task list & milestone tracking
├── pyproject.toml            # Build system and package metadata (Poetry / Hatch / Flit / Setuptools)
├── README.md                 # User-facing documentation & quickstart examples
├── src/
│   └── regexml/
│       ├── __init__.py       # Top-level API exports
│       ├── extractor.py      # Core regex extraction logic
│       ├── nested.py         # Nested tag depth-counter scanner
│       ├── attributes.py     # Resilient attribute parser
│       ├── models.py         # TagMatch and result data structures
│       └── utils.py          # String cleanups and helper utilities
└── tests/
    ├── __init__.py
    ├── test_basic.py         # Standard valid XML tests
    ├── test_malformed.py     # Broken/incomplete XML tests
    ├── test_nested.py        # Nested tag matching tests
    ├── test_attributes.py    # Tag attributes tests
    └── test_llm_outputs.py   # LLM pseudo-XML extraction tests
```

---

## 8. Verification & Acceptance Criteria

1. **Unit Test Coverage:** > 90% code coverage across valid, edge-case, and completely broken XML samples.
2. **Zero False Crashes:** Library should never raise unhandled exceptions on invalid XML strings; it must return empty lists/default values gracefully.
3. **Performance:** Sub-millisecond extraction for typical strings (< 100KB); streaming/chunked helper for multi-megabyte inputs.
4. **Python Compatibility:** Tested on Python 3.9, 3.10, 3.11, 3.12, and 3.13.
