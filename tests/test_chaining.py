"""Tests for method chaining and path-based navigation."""

import unittest
from regexml import XMLText


class TestMethodChaining(unittest.TestCase):
    def test_method_chaining_success(self):
        xml = """
        <data>
            <account>
                <profile>
                    <first_name>Ishan</first_name>
                    <last_name>Jain</last_name>
                </profile>
            </account>
        </data>
        """
        doc = XMLText(xml)
        first_name = doc.tagvalue("data").tagvalue("account").tagvalue("profile").tagvalue("first_name")
        self.assertEqual(first_name, "Ishan")
        self.assertIsInstance(first_name, XMLText)

    def test_path_drilldown_slash(self):
        xml = """
        <response>
            <payload>
                <user>
                    <username>codewizard</username>
                </user>
            </payload>
        </response>
        """
        doc = XMLText(xml)
        # Using slash notation
        username = doc.tagvalue("payload/user/username")
        self.assertEqual(username, "codewizard")

    def test_path_drilldown_dot(self):
        xml = "<root><config><env>production</env></config></root>"
        doc = XMLText(xml)
        # Using dot notation
        env = doc.tagvalue("config.env")
        self.assertEqual(env, "production")

    def test_safe_chaining_missing_intermediate_tag(self):
        xml = "<root><user><name>Alice</name></user></root>"
        doc = XMLText(xml)
        # <non_existent> is missing; must not raise AttributeError
        res = doc.tagvalue("user").tagvalue("non_existent").tagvalue("target", default="Fallback")
        self.assertEqual(res, "Fallback")

    def test_safe_chaining_falsy_behavior(self):
        xml = "<root></root>"
        doc = XMLText(xml)
        res = doc.tagvalue("missing")
        self.assertFalse(res)  # falsy
        self.assertTrue(res.is_none)


if __name__ == "__main__":
    unittest.main()
