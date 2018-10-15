import abc
import random
from math import floor
from operator import itemgetter

from tag_a_day.log import logger


class Service(object):
    name = None
    prompt_text = "Propose a value for the '{0}' tag: "

    def __init__(self, session, table, cache):
        self._session = session
        self._proposals = table
        self._cache = cache

        self._proposer = self._session().client('sts').get_caller_identity().get('Arn')

    def __repr__(self):
        return self.name

    def _get_vpc_info(self, vpc_id, region):
        # Get VPC information
        vpc = self._cache.vpc(vpc_id, region)
        vpc_name = [t for t in vpc.tags if t['Key'] == 'Name'][0]['Value']
        return vpc.id, vpc_name, vpc

    def _build_tag_sets(self, expected_tags, tags):
        instance_info = [('Tag.' + t['Key'], t['Value']) for t in tags]
        instance_info.sort(key=itemgetter(0))

        # Compute missing tags
        instance_tags = [tag['Key'] for tag in tags]
        missing_tags = [
            tag for tag in expected_tags if tag not in instance_tags]

        return instance_info, missing_tags

    def _random_choose(self, items):
        for choice in random.choices(items, k=floor(len(items) * 0.6)):
            yield choice

    def run(self, expected_tags, region, session, proposals):
        logger().info("Auditing in region: {region}".format(region=region))
        with self._proposals.batch_writer() as proposals:
            for item in self.handler(expected_tags, region, session, self._cache, proposals):
                item['resource_type'] = self.name
                item['proposer'] = self._proposer
                proposals.put_item(Item=item)

    @abc.abstractmethod
    def handler(self, expected_tags, region, session, cache, proposals):
        raise NotImplementedError
