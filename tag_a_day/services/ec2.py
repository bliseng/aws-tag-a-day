from prompt_toolkit import prompt
from tabulate import tabulate

from tag_a_day.services.service import Service


class EC2TagHandler(Service):
    name = 'ec2_instance'
    missing_tags_text = "This instance is missing '{0}' in its tags."

    def handler(self, expected_tags, region, session, cache, proposals):
        for instance in session.resource('ec2').instances.all():

            # Get VPC info
            _, vpc_name, vpc = self._get_vpc_info(
                vpc_id=instance.vpc_id,
                region=region
            )

            # Build table for displaying instance information
            instance_info, missing_tags = \
                self._build_tag_sets(expected_tags, instance.tags)

            print(tabulate(
                [
                    ("Vpc", vpc_name),
                    ("VpcID", vpc.id),
                    ("InstanceId", instance.id)
                ] + instance_info
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
                        'resource_id': instance.id,
                        'tag_key': new_tag_key,
                        'tag_value': new_tag_value,
                    }

            # Propose new tags to dynamodb

        print("\n\n")
