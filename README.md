# regexml 🚀

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A lightweight, fault-tolerant, text-first XML extraction library for Python.

Unlike traditional XML parsers (`xml.etree.ElementTree`, `lxml`) that enforce strict document validation and crash with `ParseError` on incomplete or malformed markup, **`regexml`** treats XML purely as plain text. It extracts values directly using regular expressions and resilient pattern matching.

---

## 🌟 Why `regexml`?

- **Fault-Tolerant & Resilient:** Doesn't crash on unescaped `&`, `<`, `>`, missing closing tags, or broken XML headers.
- **Perfect for LLM Outputs:** Cleanly extract tags like `<thought>`, `<answer>`, or `<code>` from AI responses.
- **Fluent Dot-Syntax Chaining:** Call `data.tagvalue("div").tagvalue("name")` seamlessly.
- **Balanced Outermost Tag Extraction:** Accurately captures outer tags with nested tags of the same name without premature cut-offs.
- **Truncated Stream Recovery:** If an XML stream cuts off prematurely (e.g. at line 1000 of 1200), it safely captures data up to EOF without failing.
- **Tag Inspector & Hierarchy:** Built-in `check_tags()` discovers all tags, reports unclosed/truncated tags, and renders visual ASCII trees.
- **Zero Heavy Dependencies:** Built 100% on Python standard library.

---

## 📦 Installation

```bash
pip install regexml
```

---

## ⚡ Quick Start

### 1. Fluent Dot-Syntax (`XMLText`)

Wrap any string with `XMLText` to unlock dot-methods while retaining 100% string compatibility:

```python
from regexml import XMLText

raw_data = """
<article id="101">
    <title>Resilient XML Extraction</title>
    <author>
        <first_name>Ishan</first_name>
        <last_name>Jain</last_name>
    </author>
</article>
"""

doc = XMLText(raw_data)

# Extract single tag value:
print(doc.tagvalue("title"))
# Output: Resilient XML Extraction

# Method Chaining:
print(doc.tagvalue("author").tagvalue("first_name"))
# Output: Ishan

# Path Shorthand:
print(doc.tagvalue("author/last_name"))
# Output: Jain
```

### 2. Functional API (Without Wrapping)

```python
from regexml import tagvalue, tagvalues

data = "<user><name>Alice</name><name>Bob</name></user>"

print(tagvalue(data, "name"))        # Alice
print(tagvalues(data, "name"))       # ['Alice', 'Bob']
```

---

## 🎯 Advanced Features

### Balanced Nested Tags of the Same Name
Standard regex chops off at the first closing tag. `regexml` tracks depth counter to return the true balanced outermost tag:

```python
xml = """
<div id="outer">
    Hello
    <div id="inner">World</div>
    Welcome!
</div>
"""
doc = XMLText(xml)
print(doc.tagvalue("div"))
# Output:
# Hello
# <div id="inner">World</div>
# Welcome!
```

### Truncated / Broken XML Recovery
If your XML was cut off mid-stream (e.g., from network drop or LLM token limit):

```python
truncated_xml = "<user><id>123</id><bio>Software engineer who loves Python... [CUT OFF]"
doc = XMLText(truncated_xml)

bio = doc.tagvalue("bio")
print(bio)                  # "Software engineer who loves Python... [CUT OFF]"
print(bio.is_truncated)     # True
```

### Tag Inspection & Broken Markup Detection (`check_tags`)

```python
report = doc.check_tags()

# View all tags found:
print(report.tags)          # ['user', 'id', 'bio']

# Pinpoint unclosed tags (truncated points):
print(report.unclosed_tags) # ['user', 'bio']

# Print terminal ASCII tree:
print(report.tree())
```

---

## 📄 License

MIT License. Developed by Ishan.
