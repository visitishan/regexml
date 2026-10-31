"""Tests for nested XML tags with identical names."""

import unittest
from regexml import XMLText, tagvalue, tagvalues


class TestNestedExtraction(unittest.TestCase):
    def test_balanced_nested_tags_outermost(self):
        xml = """
        <div class="outer">
            Outer content before
            <div class="inner">
                Inner content
            </div>
            Outer content after
        </div>
        """
        doc = XMLText(xml)
        extracted = doc.tagvalue("div")

        # The extracted content must contain BOTH inner and outer parts
        self.assertIn("Outer content before", extracted)
        self.assertIn('<div class="inner">', extracted)
        self.assertIn("Inner content", extracted)
        self.assertIn("Outer content after", extracted)

    def test_multiple_sibling_nested_tags(self):
        xml = """
        <section>
            <div>
                Block 1
                <div>Nested in 1</div>
            </div>
            <div>
                Block 2
                <div>Nested in 2</div>
            </div>
        </section>
        """
        blocks = tagvalues(xml, "div")
        self.assertEqual(len(blocks), 2)
        self.assertIn("Block 1", blocks[0])
        self.assertIn("Nested in 1", blocks[0])
        self.assertIn("Block 2", blocks[1])
        self.assertIn("Nested in 2", blocks[1])

    def test_nested_with_inner_stripped(self):
        xml = "<div>Outer <div>Inner</div> Finish</div>"
        clean_text = tagvalue(xml, "div", strip_inner_tags=True)
        self.assertEqual(clean_text, "Outer Inner Finish")


if __name__ == "__main__":
    unittest.main()
