from unittest import TestCase

from tag_a_day.config import Configuration


class TestConfiguration(TestCase):
    def test_process_list(self):
        cfg = Configuration(None)

        actual = cfg.process_list([1, 2, 3, 4])
        self.assertEqual([1, 2, 3, 4], actual)

        actual = cfg.process_list("1,2,3,4")
        self.assertEqual(["1", "2", "3", "4"], actual)
