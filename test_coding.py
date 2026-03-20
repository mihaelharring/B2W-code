import json
import os
import tempfile
import unittest

import index


class CodingTests(unittest.TestCase):
    def test_parse_questions_json_list(self):
        data = [
            {"question": "Q1", "choices": ["A", "B", "C", "D"], "answer": "a"},
            {"question": "Q2", "options": {"a": "A", "b": "B"}, "answer": "b"}
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            path = f.name

        try:
            q = index.parse_questions_file(path)
            self.assertEqual(len(q), 2)
            self.assertEqual(q[0]["question"], "Q1")
            self.assertEqual(q[0]["options"], {"a": "A", "b": "B", "c": "C", "d": "D"})
            self.assertEqual(q[1]["answer"], "b")
        finally:
            os.remove(path)

    def test_parse_questions_json_object(self):
        data = {"questions": [{"question": "Q3", "choices": ["X", "Y"], "answer": "a"}]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            path = f.name

        try:
            q = index.parse_questions_file(path)
            self.assertEqual(q[0]["question"], "Q3")
            self.assertEqual(q[0]["options"], {"a": "X", "b": "Y"})
        finally:
            os.remove(path)

    def test_clean_down_options_basic(self):
        opts = {"a": "a) apple", "b": " b) banana", "c": "pear"}
        cleaned = index.clean_down_options(opts)
        self.assertEqual(cleaned, {"a": "apple", "b": "banana", "c": "pear"})

    def test_get_random_question(self):
        q1 = {"question": "Q", "options": {"a": "A"}, "answer": "a"}
        self.assertIn(index.get_random_question([q1]), [q1])


if __name__ == "__main__":
    unittest.main()
