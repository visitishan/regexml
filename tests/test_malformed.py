"""Tests for malformed, broken, and truncated XML."""

import unittest
from regexml import XMLText, tagvalue, tagvalues


class TestMalformedExtraction(unittest.TestCase):
    def test_truncated_xml_graceful_recovery(self):
        # XML cut off mid-stream (e.g. line 1000 cutoff)
        truncated = """
        <response>
            <status>200</status>
            <data>
                <item>Valid Item 1</item>
                <item>Valid Item 2</item>
                <summary>This is a long summary that was abruptly cut off... [EOF reached]
        """
        doc = XMLText(truncated)

        # Fully closed earlier tags work normally
        self.assertEqual(doc.tagvalue("status"), "200")
        items = doc.tagvalues("item")
        self.assertEqual(items, ["Valid Item 1", "Valid Item 2"])

        # Cutoff tag <summary> without </summary> extracts up to EOF
        summary = doc.tagvalue("summary", allow_unclosed=True)
        self.assertIsNotNone(summary)
        self.assertIn("abruptly cut off", summary)
        self.assertTrue(summary.is_truncated)

    def test_unescaped_special_characters(self):
        # Traditional parsers crash on raw & and < inside content
        xml = "<message>Comparison: x < y & a > b are common symbols.</message>"
        val = tagvalue(xml, "message")
        self.assertEqual(val, "Comparison: x < y & a > b are common symbols.")

    def test_unquoted_and_messy_attributes(self):
        xml = "<input id=username class='input-box' disabled data-value=\"secret\">user input</input>"
        val = tagvalue(xml, "input")
        self.assertEqual(val, "user input")

    def test_no_root_element_multiple_fragments(self):
        # Mixed plain text and XML tags (common in LLM outputs)
        llm_output = """
        Sure! Here is the plan you asked for:
        <thought>
            The user wants a Python script to parse logs.
        </thought>
        And here is the answer:
        <answer>
            Run `python script.py` to get started.
        </answer>
        Let me know if you need more help!
        """
        doc = XMLText(llm_output)
        thought = doc.tagvalue("thought")
        answer = doc.tagvalue("answer")

        self.assertEqual(thought, "The user wants a Python script to parse logs.")
        self.assertEqual(answer, "Run `python script.py` to get started.")


if __name__ == "__main__":
    unittest.main()
