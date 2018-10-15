from boto3.dynamodb.conditions import Key

from tag_a_day.actions import Action


class Reconcile(Action):
    def __init__(self, service, proposals):
        self._resource_type = service
        self._proposals = proposals

    def run(self):
        # Get a list of all tags for this service
        result = self._proposals.query(
            TableName=self._proposals.table_name,
            IndexName='proposer-resource_type',
            KeyConditionExpression=Key('resource_type').eq(self._resource_type)
        )

        result
        # Sort the tag sets into groups per resource_id
        pass
