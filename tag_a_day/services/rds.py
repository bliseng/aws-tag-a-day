from prompt_toolkit import prompt
from tabulate import tabulate

from tag_a_day.services.service import Service


class RDSTagHandler(Service):
    name = 'rds_instance'
    missing_tags_text = "This instance is missing '{0}' in its tags"

    def handler(self, expected_tags, region, session, cache, proposals):
        rds = session.client('rds')
        paginator = rds. \
            get_paginator('describe_db_instances'). \
            paginate()
        for instances_page in paginator:
            # Randomly pick 2/3rds of the nodes
            for instance in self._random_choose(instances_page['DBInstances']):

                # Get VPC info
                _, vpc_name, vpc = self._get_vpc_info(
                    vpc_id=instance['DBSubnetGroup']['VpcId'],
                    region=region
                )

                # Build table for displaying instance information
                tags = rds.list_tags_for_resource(
                    ResourceName=instance['DBInstanceArn']).get('TagList')
                instance_info, missing_tags = \
                    self._build_tag_sets(expected_tags, tags)

                print(tabulate(
                    [
                        ("Vpc", vpc_name),
                        ("VpcID", vpc.id),
                        ("DatabaseARN", instance['DBInstanceArn']),
                    ] + instance_info
                ))

                if any(missing_tags):
                    print(self.missing_tags_text.format(
                        "','".join(missing_tags)))

                    # Build padding for easier to read prompt
                    longest_key = len(max(missing_tags, key=len))
                    justify_length = len(self.prompt_text) + longest_key

                    new_tags = {}
                    for tag_key in missing_tags:
                        new_tag_value = prompt(self.prompt_text.format(
                            tag_key).ljust(justify_length))
                        new_tags[tag_key] = new_tag_value

                    for new_tag_key, new_tag_value in new_tags.items():
                        yield {
                            'resource_id': instance.id,
                            'tag_key': new_tag_key,
                            'tag_value': new_tag_value,
                        }
