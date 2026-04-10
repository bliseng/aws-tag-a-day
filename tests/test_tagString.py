from unittest import TestCase

from tag_a_day.tag_types import TagString


class TestTagString(TestCase):
    def test_validate(self):
        self.assertTrue(TagString("mock").withValue("value").validate())
        self.assertFalse(TagString(1).validate())
        self.assertFalse(TagString([]).validate())
