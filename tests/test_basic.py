"""Basic extraction tests for regexml."""

import unittest
from regexml import XMLText, tagvalue, tagvalues, extract_tags


class TestBasicExtraction(unittest.TestCase):
    def test_basic_tagvalue_function(self):
        xml = "<user><name>John Doe</name><age>30</age></user>"
        self.assertEqual(tagvalue(xml, "name"), "John Doe")
        self.assertEqual(tagvalue(xml, "age"), "30")
        self.assertEqual(tagvalue(xml, "missing", default="N/A"), "N/A")

    def test_basic_tagvalues_function(self):
        xml = "<items><item>Apple</item><item>Banana</item><item>Cherry</item></items>"
        items = tagvalues(xml, "item")
        self.assertEqual(items, ["Apple", "Banana", "Cherry"])
        self.assertEqual(len(items), 3)

    def test_xml_text_wrapper_dot_syntax(self):
        xml = "<post><title>Hello World</title><content>This is a test post.</content></post>"
        doc = XMLText(xml)
        self.assertEqual(doc.tagvalue("title"), "Hello World")
        self.assertEqual(doc.tagvalue("content"), "This is a test post.")
        self.assertEqual(doc.tagvalue("title").upper(), "HELLO WORLD")
        self.assertEqual(len(doc.tagvalue("title")), 11)

    def test_include_tags_option(self):
        xml = "<msg><b>Important</b> text</msg>"
        res = tagvalue(xml, "msg", include_tags=True)
        self.assertEqual(res, "<msg><b>Important</b> text</msg>")

    def test_strip_inner_tags(self):
        xml = "<msg><b>Important</b> <i>text</i></msg>"
        res = tagvalue(xml, "msg", strip_inner_tags=True)
        self.assertEqual(res, "Important text")

    def test_attribute_filtering(self):
        xml = """
        <response>
            <data type="summary">Summary Info</data>
            <data type="details">Detailed Info</data>
        </response>
        """
        summary = tagvalue(xml, "data", match_attributes={"type": "summary"})
        details = tagvalue(xml, "data", match_attributes={"type": "details"})
        self.assertEqual(summary, "Summary Info")
        self.assertEqual(details, "Detailed Info")

    def test_cdata_handling(self):
        xml = "<description><![CDATA[Some <raw> characters & code]]></description>"
        val = tagvalue(xml, "description")
        self.assertEqual(val, "Some <raw> characters & code")

    def test_batch_extract_tags(self):
        xml = "<order><id>101</id><status>Shipped</status><item>Item 1</item><item>Item 2</item></order>"
        extracted = extract_tags(xml, ["id", "status", "item"])
        self.assertEqual(extracted["id"], ["101"])
        self.assertEqual(extracted["status"], ["Shipped"])
        self.assertEqual(extracted["item"], ["Item 1", "Item 2"])


if __name__ == "__main__":
    unittest.main()
