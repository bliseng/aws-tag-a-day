from tag_a_day.config import Configuration
from tag_a_day.services.service import Service


class EMRTagHandler(Service):
    name = 'emr_cluster'
    missing_tags_text = "This EMR cluster is missing '{0}' in its tags."

    def resources(self, session, resource_ids):
        emr = session.client('emr')
        if resource_ids is not None:
            for resource in Configuration.process_list(resource_ids):
                yield emr.describe_cluster(
                    ClusterId=resource
                ).get('Cluster')
        else:
            for emr_page in emr.get_paginator('list_clusters').paginate():
                for cluster_summary in self._random_choose(emr_page['Clusters']):
                    yield emr.describe_cluster(
                        ClusterId=cluster_summary['Id']).get('Cluster')

    def handler(self, cluster, expected_tags, region, session, cache, proposals):
        # Get VPC info
        subnet = self._cache.subnet(
            cluster['Ec2InstanceAttributes']['Ec2SubnetId'],
            region
        )
        _, vpc_name, vpc = self._get_vpc_info(
            vpc_id=subnet.vpc_id,
            region=region
        )

        # Build table for displaying instance information
        evaluated_tags = self._progress.evaluated_tags(cluster['Id'])
        instance_info, missing_tags = \
            self._build_tag_sets(expected_tags, evaluated_tags, cluster['Tags'])

        if self._progress.has_finished(cluster['Id'], expected_tags):
            self._skip(cluster['Id'])
            return

        if any(missing_tags):
            self._print_table(
                ("Vpc", vpc_name),
                ("VpcID", vpc.id),
                ("ClusterID", cluster['Id']),
                *instance_info
            )

            if self._user_skip():
                return

            tag_prompt = self._build_tag_prompt(missing_tags)
            for tag_key in missing_tags:
                yield {
                    'resource_id': cluster['Id'],
                    'tag_key': tag_key,
                    'tag_value': tag_prompt(tag_key),
                }
