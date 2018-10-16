from tag_a_day.config import Configuration
from tag_a_day.services.service import Service


class RDSTagHandler(Service):
    name = 'rds_instance'
    missing_tags_text = "This instance is missing '{0}' in its tags"

    def resources(self, session, resource_ids):
        page_args = {}
        if resource_ids is not None:
            page_args['Filters'] = [{
                'Name': 'db-instance-id',
                'Values': resource_ids
            }]

        rds = session.client('rds')
        paginator = rds. \
            get_paginator('describe_db_instances'). \
            paginate(**page_args)
        for instances_page in paginator:
            # Randomly pick 2/3rds of the nodes
            for instance in self._random_choose(instances_page['DBInstances']):
                instance['Tags'] = rds.list_tags_for_resource(
                    ResourceName=instance['DBInstanceArn']).get('TagList')
                yield instance

    def handler(self, instance, expected_tags, region, session, cache, proposals):
        # Get VPC info
        _, vpc_name, vpc = self._get_vpc_info(
            vpc_id=instance['DBSubnetGroup']['VpcId'],
            region=region
        )

        # Build table for displaying instance information
        evaluated_tags = self._progress.evaluated_tags(instance['DbiResourceId'])
        instance_info, missing_tags = \
            self._build_tag_sets(expected_tags, evaluated_tags, instance['Tags'])

        if self._progress.has_finished(instance['DbiResourceId'], expected_tags):
            self._skip(instance['DbiResourceId'])
            return

        if any(missing_tags):
            self._print_table(
                ("Vpc", vpc_name),
                ("VpcID", vpc.id),
                ("DatabaseARN", instance['DBInstanceArn']),
                *instance_info
            )

            if self._user_skip():
                return

            tag_prompt = self._build_tag_prompt(missing_tags)
            for tag_key in missing_tags:
                yield {
                    'resource_id': instance['DbiResourceId'],
                    'tag_key': tag_key,
                    'tag_value': tag_prompt(tag_key),
                }
