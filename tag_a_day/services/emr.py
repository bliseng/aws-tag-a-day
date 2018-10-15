from prompt_toolkit import prompt
from tabulate import tabulate

from tag_a_day.services.service import Service


class EMRTagHandler(Service):
    name = 'emr_cluster'
    missing_tags_text = "This EMR cluster is missing '{0}' in its tags."

    def handler(self, expected_tags, region, session, cache, proposals):
        emr = session.client('emr')
        for emr_page in emr.get_paginator('list_clusters').paginate():
            # Randomly pick 2/3rds of the nodes
            for cluster_summary in self._random_choose(emr_page['Clusters']):
                cluster = emr.describe_cluster(
                    ClusterId=cluster_summary['Id']).get('Cluster')

                # Get VPC info
                subnet = self._cache.subnet(
                    cluster['Ec2InstanceAttributes']['Ec2SubnetId'], region)
                _, vpc_name, vpc = self._get_vpc_info(
                    vpc_id=subnet.vpc_id,
                    region=region
                )

                instance_info, missing_tags = \
                    self._build_tag_sets(expected_tags, cluster['Tags'])

                print(tabulate(
                    [
                        ("Vpc", vpc_name),
                        ("VpcID", vpc.id),
                        ("ClusterID", cluster_summary['Id']),
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
                            'resource_id': cluster_summary['Id'],
                            'tag_key': new_tag_key,
                            'tag_value': new_tag_value,
                        }
