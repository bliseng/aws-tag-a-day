from boto3.dynamodb.conditions import Key


class AWSCache(object):
    def __init__(self, session_function):
        self._session = lambda region: session_function(region)
        self._cache_store = {}

    def vpc(self, vpc_id, region):
        if vpc_id not in self._cache('vpc'):
            vpc = self._session(region).resource('ec2').Vpc(vpc_id)
            self._set_cache('vpc', vpc.id, vpc)
        return self._get_cache('vpc', vpc_id)

    def subnet(self, subnet_id, region):
        if subnet_id not in self._cache('subnet'):
            subnet = self._session(region).resource('ec2').Subnet(subnet_id)
            self._set_cache('subnet', subnet.id, subnet)
        return self._get_cache('subnet', subnet_id)

    def _cache(self, cache_id):
        if cache_id not in self._cache_store:
            self._cache_store[cache_id] = {}
        return self._cache_store[cache_id]

    def _set_cache(self, cache_id, object_id, cache_object):
        self._cache(cache_id)  # Ensure the cache exists
        self._cache_store[cache_id][object_id] = cache_object

    def _get_cache(self, cache_id, object_id):
        cache = self._cache(cache_id)
        return cache.get(object_id, None)


class ProgressCache(object):
    def __init__(self, table, proposer, resource_type):
        self._proposals = table
        self._proposer = proposer
        self._resource_type = resource_type
        self._progress_items = []

    def load(self):
        result = self._proposals.query(
            TableName=self._proposals.table_name,
            IndexName='proposer-resource_type',
            KeyConditionExpression=Key('proposer').eq(self._proposer) & Key('resource_type').eq(self._resource_type)
        )
        for item in result['Items']:
            del item['proposer']
            del item['resource_type']
            self._progress_items.append(item)
        return self

    def has_finished(self, resource_id, tag_names):
        evaluated_tags = self.evaluated_tags(resource_id)
        return set(tag_names) == set(evaluated_tags)

    def evaluated_tags(self, resource_id):
        return list(map(
            lambda r: r['tag_key'],
            filter(
                lambda r: r['resource_id'] == resource_id,
                self._progress_items)
        ))
