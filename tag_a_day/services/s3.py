from tag_a_day.services.service import Service


class S3TagHandler(Service):
    name = 's3'
    missing_tags_text = "This bucket is missing '{0}' in its tags."

    def resources(self, session):
        return session.resource('s3').buckets.all()

    def handler(self, bucket, expected_tags, region, session, cache, proposals):
        try:
            tags = bucket.Tagging().tag_set
        except Exception:
            tags = []

        # Build table for displaying instance information
        evaluated_tags = self._progress.evaluated_tags(bucket.name)
        bucket_info, missing_tags = \
            self._build_tag_sets(expected_tags, evaluated_tags, tags)

        if self._progress.has_finished(bucket.name, expected_tags):
            self._skip(bucket.name)
            return

        if any(missing_tags):
            self._print_table(
                ("BucketName", bucket.name),
                *bucket_info
            )

            tag_prompt = self._build_tag_prompt(missing_tags)
            for tag_key in missing_tags:
                yield {
                    'resource_id': bucket.name,
                    'tag_key': tag_key,
                    'tag_value': tag_prompt(tag_key)
                }
