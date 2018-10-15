from prompt_toolkit import prompt
from tabulate import tabulate

from tag_a_day.services.service import Service


class S3TagHandler(Service):
    name = 's3'
    missing_tags_text = "This bucket is missing '{0}' in its tags."

    def handler(self, expected_tags, region, session, cache, proposals):
        for bucket in session.resource('s3').buckets.all():
            try:
                tags = bucket.Tagging().tag_set
            except Exception:
                tags = []
            bucket_info, missing_tags = \
                self._build_tag_sets(expected_tags, tags)

            print(tabulate(
                [
                    ("BucketName", bucket.name)
                ] + bucket_info
            ))

            if any(missing_tags):
                print(self.missing_tags_text.format("','".join(missing_tags)))

                # Build padding for easier to read prompt
                longest_key = len(max(missing_tags, key=len))
                justify_length = len(self.prompt_text) + longest_key

                new_tags = {}
                for tag_key in missing_tags:
                    new_tags[tag_key] = prompt(
                        self.prompt_text.format(tag_key).ljust(justify_length))

                for new_tag_key, new_tag_value in new_tags.items():
                    yield {
                        'resource_id': bucket.name,
                        'tag_key': new_tag_key,
                        'tag_value': new_tag_value
                    }
