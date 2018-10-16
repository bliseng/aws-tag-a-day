import abc
import sys
from operator import itemgetter
from tabulate import tabulate
from tag_a_day.cache import ProgressCache
from tag_a_day.log import logger

try:
    input = raw_input
except NameError:
    pass


class Service(object):
    name = None
    prompt_text = "Propose a value for the '{0}' tag: "
    skip_text = "Skipping '{0}' as it has been evaluated\n\n"
    missing_tags_text = ''

    def __init__(self, session, table, cache):
        self._session = session
        self._proposals = table
        self._cache = cache
        self._proposer = ''
        self._progress = None

    def load(self):
        self._proposer = self._session().client('sts').get_caller_identity().get('Arn')
        self._progress = ProgressCache(self._proposals, self._proposer, self.name).load()
        return self

    def __repr__(self):
        return self.name

    def _get_vpc_info(self, vpc_id, region):
        # Get VPC information
        vpc = self._cache.vpc(vpc_id, region)
        vpc_name = [t for t in vpc.tags if t['Key'] == 'Name'][0]['Value']
        return vpc.id, vpc_name, vpc

    def _build_tag_sets(self, expected_tags, evaluated_tags, tags):
        instance_info = [('Tag.' + t['Key'], t['Value']) for t in tags]
        instance_info.sort(key=itemgetter(0))

        # Compute missing tags
        instance_tags = [tag['Key'] for tag in tags] + evaluated_tags
        missing_tags = [
            tag for tag in expected_tags if (tag not in instance_tags)]

        return instance_info, missing_tags

    def _random_choose(self, items):
        return items
        # for choice in random.choices(items, k=floor(len(items) * 0.6)):
        #     yield choice

    def _print_table(self, *args):
        print(tabulate(args))

    def _skip(self, resource_id):
        print(self.skip_text.format(resource_id))

    def _build_tag_prompt(self, missing_tags):
        sys.stdout.write(self.missing_tags_text.format(
            "','".join(missing_tags)))

        # Build padding for easier to read prompt
        longest_key = len(max(missing_tags, key=len))
        justify_length = len(self.prompt_text) + longest_key

        def tag_prompt(tag_key):
            sys.stdout.write(self.prompt_text.format(
                tag_key).ljust(justify_length))
            sys.stdout.flush()
            response = input()
            if len(response) < 1:
                print("Tag must not be empty")
                return tag_prompt(tag_key)
            else:
                return response

        return tag_prompt

    def run(self, expected_tags, region, session):
        logger().info("Auditing in region: {region}".format(region=region))
        with self._proposals.batch_writer() as proposals:
            for resource in self.resources(session):
                handled_tag = False
                for item in self.handler(resource, expected_tags, region, session, self._cache, proposals):
                    handled_tag = True
                    item['resource_type'] = self.name
                    item['proposer'] = self._proposer
                    proposals.put_item(Item=item)
                if handled_tag:
                    print("\n\n")

    @abc.abstractmethod
    def resources(self, session):
        raise NotImplementedError

    @abc.abstractmethod
    def handler(self, resource, expected_tags, region, session, cache, proposals):
        raise NotImplementedError
