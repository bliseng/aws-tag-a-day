from unittest import TestCase

from tag_a_day.tag_types import TagCategorical


class TestTagCategorical(TestCase):
    def test_validate(self):
        self.assertTrue(TagCategorical("mock", ["foo", "hallo", "bar"]).withValue("hallo").validate())
        self.assertFalse(TagCategorical(1, []).validate())
        self.assertFalse(TagCategorical([], []).validate())
