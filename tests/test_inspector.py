"""Tests for tag inspection and hierarchy reporting."""

import unittest
from regexml import XMLText, check_tags


class TestInspector(unittest.TestCase):
    def test_tag_discovery_and_counts(self):
        xml = """
        <catalog>
            <item><id>1</id><price>10</price></item>
            <item><id>2</id><price>20</price></item>
        </catalog>
        """
        report = check_tags(xml)
        self.assertEqual(set(report.tags), {"catalog", "item", "id", "price"})
        self.assertEqual(report.tag_counts["item"], 2)
        self.assertEqual(report.tag_counts["id"], 2)
        self.assertEqual(report.tag_counts["price"], 2)
        self.assertEqual(report.unclosed_tags, [])

    def test_unclosed_tags_detection(self):
        # Truncated markup where catalog and item were never closed
        broken_xml = """
        <catalog>
            <item>
                <id>101</id>
                <price>99.99</price>
        """
        doc = XMLText(broken_xml)
        report = doc.check_tags()

        # Must accurately flag catalog and item as unclosed!
        self.assertIn("catalog", report.unclosed_tags)
        self.assertIn("item", report.unclosed_tags)
        self.assertNotIn("id", report.unclosed_tags)
        self.assertNotIn("price", report.unclosed_tags)

    def test_tree_rendering(self):
        xml = """
        <root>
            <branch>
                <leaf>Content</leaf>
            </branch>
        </root>
        """
        report = check_tags(xml)
        tree_output = report.tree()

        self.assertIn("root", tree_output)
        self.assertIn("branch", tree_output)
        self.assertIn("leaf", tree_output)
        self.assertTrue("└──" in tree_output or "├──" in tree_output)


if __name__ == "__main__":
    unittest.main()
