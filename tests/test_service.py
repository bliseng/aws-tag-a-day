from unittest import TestCase

from tag_a_day.services.service import Service


class TestService(TestCase):
    def test__build_tag_sets(self):
        src = Service(None, None, None)
        _, missing_tags = src._build_tag_sets(
            expected_tags=['a', 'b', 'c', 'd', 'e'],
            evaluated_tags=['c'],
            tags=[
                {'Key': 'a', 'Value': '1'},
                {'Key': 'b', 'Value': '2'}
            ]
        )

        self.assertEqual(missing_tags, ['d', 'e'])
