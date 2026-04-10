import json
from unittest import TestCase

from tag_a_day.config import Configuration
from tag_a_day.tag_types import TagString, TagCategorical


class TestConfiguration(TestCase):
    def test_process_list(self):
        cfg = Configuration(None)

        actual = cfg.process_list([1, 2, 3, 4])
        self.assertEqual([1, 2, 3, 4], actual)

        actual = cfg.process_list("1,2,3,4")
        self.assertEqual(["1", "2", "3", "4"], actual)

    def test_process_tag_list(self):
        cfg = Configuration(None)

        actual = cfg.process_tag_list([1, 2, 3, 4])
        self.assertEqual([
            TagString(1),
            TagString(2),
            TagString(3),
            TagString(4)
        ], actual)

        actual = cfg.process_tag_list("1,2,3,4")
        self.assertEqual([
            TagString("1"),
            TagString("2"),
            TagString("3"),
            TagString("4")
        ], actual)

        actual = cfg.process_tag_list(json.dumps([
            {'key': '1'},
            {'key': '2'},
            {'key': '3'},
            {'key': '4'}
        ]))
        self.assertEqual([
            TagString('1'),
            TagString('2'),
            TagString('3'),
            TagString('4')
        ], actual)

        actual = cfg.process_tag_list([
            {'key': '1'},
            {'key': '2'},
            {'key': '3'},
            {'key': '4'}
        ])
        self.assertEqual([
            TagString('1'),
            TagString('2'),
            TagString('3'),
            TagString('4')
        ], actual)

        actual = cfg.process_tag_list(json.dumps([
            {'key': '1', 'categories': ['a', 'b']},
            {'key': '2', 'categories': ['1', '2']},
            {'key': '3'},
            {'key': '4'}
        ]))
        self.assertEqual([
            TagCategorical('1', ['a', 'b']),
            TagCategorical('2', ['1', '2']),
            TagString('3'),
            TagString('4')
        ], actual)
