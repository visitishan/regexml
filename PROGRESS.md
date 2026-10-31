# Project Progress & Roadmap: `regexml`

This document tracks the end-to-end development lifecycle of the **`regexml`** library. Use this checklist to monitor current progress, upcoming milestones, and completed features.

---

## 📊 Overall Progress Summary

| Metric | Status |
|---|---|
| **Current Phase** | Phase 1: Planning & Architecture Setup |
| **Overall Completion** | 15% |
| **Target Python Version** | Python 3.9+ |
| **Dependencies** | Python Standard Library (`re`, `typing`, `dataclasses`) |

---

## 🗺️ Development Phases

### Phase 1: Specification & Project Foundation ⏳ (In Progress)
- [x] Create Technical Specification document (`SPECIFICATION.md`)
- [x] Create Progress Tracking document (`PROGRESS.md`)
- [ ] Initialize Python package layout (`src/regexml/`, `tests/`)
- [ ] Create `pyproject.toml` with build metadata, dependencies, and linting tools
- [ ] Create initial `README.md` with problem statement and planned syntax

---

### Phase 2: Core Regex Extraction Engine ⏹️ (Pending)
- [ ] Implement data structures (`TagMatch`) in `models.py`
- [ ] Implement core single-tag extractor `tagvalue(text, tag)` in `extractor.py`
- [ ] Implement multi-occurrence extractor `tagvalues(text, tag)`
- [ ] Implement `XMLText(str)` subclass wrapper for fluent dot-syntax (`my_text.tagvalue("div")`)
- [ ] Implement Method Chaining support (`my_text.tagvalue("div").tagvalue("name").tagvalue("first_name")`)
- [ ] Implement Safe Chaining (prevent `AttributeError` when intermediate tags are missing)
- [ ] Implement Path Shorthand (`my_text.tagvalue("div/name/first_name")`)
- [ ] Add basic parameters:
  - [ ] `include_tags: bool` (keep or strip surrounding `<tag>...</tag>`)
  - [ ] `strip_whitespace: bool`
  - [ ] `ignore_case: bool`
  - [ ] `multiline: bool` (DOTALL support)
- [ ] Write unit tests for standard and clean XML snippets (`test_basic.py`)

---

### Phase 3: Fault-Tolerance & Attribute Handling ⏹️ (Pending)
- [ ] Implement resilient attribute parser (`attributes.py`):
  - [ ] Support double-quoted, single-quoted, and unquoted values
  - [ ] Support boolean attributes (e.g. `<input disabled>`)
- [ ] Filter extraction by matching attributes (`match_attributes={'id': 'main'}`)
- [ ] Implement self-closing tag handling (`<tag ... />`)
- [ ] Implement `tagmatch(text, tag)` returning `TagMatch` objects
- [ ] Implement Truncated XML Graceful Recovery (`allow_unclosed=True`):
  - [ ] Extract content up to EOF or next peer tag when closing tag is missing
  - [ ] Attach `is_truncated = True` flag to matches
- [ ] Implement CDATA handling (`<![CDATA[ ... ]]>`)
- [ ] Write tests for dirty, truncated, and malformed XML (`test_malformed.py`)

---

### Phase 4: Advanced Scenarios (Nesting, Hierarchy & Inspection) ⏹️ (Pending)
- [ ] Implement balanced depth-counter scanner for identical nested tags (`nested.py`)
  - [ ] Guarantee outermost opening tag matches corresponding balanced closing tag
  - [ ] Fallback graceful slice if XML is truncated mid-nest
- [ ] Implement Tag Inspection & Hierarchy Engine (`check_tags()` in `inspector.py`):
  - [ ] Extract all distinct tags and their frequency counts
  - [ ] Identify unclosed / truncated tags via stack analysis
  - [ ] Build nested parent-child hierarchy map
  - [ ] Generate visual ASCII tree representation (`report.tree()`)
- [ ] Handle XML namespaces:
  - [ ] Strict mode (`ns:tag`)
  - [ ] Relaxed mode (match tag name regardless of namespace prefix)
- [ ] Implement batch extractor `extract_tags(text, tags=['a', 'b', 'c'])`
- [ ] Implement `strip_inner_tags: bool` to recursively remove all inner child markup
- [ ] Write tests for deeply nested, inspected, and namespaced tags (`test_nested.py`, `test_inspector.py`)

---

### Phase 5: LLM & Real-world Edge Cases ⏹️ (Pending)
- [ ] Build test suite with real LLM prompt outputs (e.g., `<thought>`, `<code>`, markdown inside XML)
- [ ] Handle unescaped characters (`<`, `>`, `&`, unclosed brackets in text)
- [ ] Add comment stripping (`ignore_comments=True`)
- [ ] Add convenience file-reading helpers (`extract_from_file(filepath, tag)`)
- [ ] Performance benchmark against typical 1MB+ text inputs

---

### Phase 6: Packaging, Documentation & Release ⏹️ (Pending)
- [ ] Write full API reference in `README.md` with copy-pasteable examples
- [ ] Setup `pytest` configuration and automated testing script
- [ ] Verify package build with `python -m build`
- [ ] Add PyPI publishing workflow / instructions
- [ ] Final code review and version `0.1.0` tag

---

## 📝 Activity & Decision Log

| Date | Activity / Decision | Status |
|---|---|---|
| **2026-10-31** | Project inception: Decided on text-first, regex-based XML extraction to handle malformed XML & LLM outputs. | Done |
| **2026-10-31** | Created `SPECIFICATION.md` detailing API signatures, regex patterns, nesting strategy, and fault tolerance. | Done |
| **2026-10-31** | Created `PROGRESS.md` to track milestones across all 6 phases. | Done |
| **2026-11-01** | Added `XMLText(str)` subclass for fluent dot-syntax (`my_text.tagvalue("div")`) and finalized Outermost Balanced Depth Scanner algorithm in spec. | Done |
| **2026-11-01** | Designed Method Chaining (`.tagvalue().tagvalue()`), Safe Chaining (no AttributeError), and Path shorthand (`"div/name/first_name"`). | Done |
| **2026-11-01** | Designed Truncated XML Graceful Recovery (`allow_unclosed=True`, `is_truncated`) and Tag Inspection & Hierarchy Engine (`check_tags()` + `.tree()`). | Done |
