from tag_a_day.config import Configuration
from tag_a_day.services.service import Service


class EC2TagHandler(Service):
    """
    Handles the tagging of EC2 instances.
    """

    name = 'ec2_instance'
    missing_tags_text = "This instance is missing '{0}' in its tags."

    def resources(self, session, resource_ids):
        instances = session.resource('ec2').instances
        if resource_ids is not None:
            return instances.filter(Filters=[{
                'Name': 'instance-id',
                'Values': resource_ids
            }])
        return instances.all()

    def handler(self, instance, expected_tags, region, session, cache, proposals):
        print("Auditing '{name}:{id}'".format(
            name=self.name,
            id=instance.id
        ))
        # Get VPC info
        if instance.vpc_id is None:
            vpc_name = 'EC2-Classic'
            vpc_id = 'EC2-Classic'
        else:
            _, vpc_name, vpc = self._get_vpc_info(
                vpc_id=instance.vpc_id,
                region=region
            )
            vpc_id = vpc.id

        # Build table for displaying instance information
        evaluated_tags = self._progress.evaluated_tags(instance.id)
        instance_info, missing_tags = \
            self._build_tag_sets(expected_tags, evaluated_tags, instance.tags)

        if self._progress.has_finished(instance.id, expected_tags):
            self._skip(instance.id)
            return

        if any(missing_tags):
            self._print_table(
                ("Vpc", vpc_name),
                ("VpcID", vpc_id),
                ("InstanceId", instance.id),
                *instance_info
            )

            tag_prompt = self._build_tag_prompt(missing_tags)
            for tag_key in missing_tags:
                yield {
                    'resource_id': instance.id,
                    'tag_key': tag_key,
                    'tag_value': tag_prompt(tag_key),
                }
