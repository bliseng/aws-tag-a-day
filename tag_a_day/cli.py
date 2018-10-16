import sys
import time

from boto3 import Session
from botocore.exceptions import ClientError

from tag_a_day.cache import AWSCache
from tag_a_day.config import Configuration
from tag_a_day.log import logger
from tag_a_day.services import Services


def _initialise_common():
    def aws_session(region='us-east-1'):
        return Session(region_name=region)

    conf = Configuration(aws_session).parse()
    return aws_session, conf


def run():
    aws_session, conf = _initialise_common()
    cache = AWSCache(aws_session)

    table = aws_session(). \
        resource('dynamodb', conf.dynamodb_table_region). \
        Table(conf.dynamodb_table_name)
    services = Services(
        session=aws_session,
        cache=cache,
        services=conf.services,
        resource_id=conf.resource_ids,
        proposals=table)

    for region in conf.regions:
        session = aws_session(region)
        for service in services:
            print(
                'Auditing tags for {0} in {1}'.format(service, region))
            service.run(
                expected_tags=conf.required_tags,
                region=region,
                session=session
            )


def initialise():
    aws_session, conf = _initialise_common()
    table_region = conf.dynamodb_table_region
    table_name = conf.dynamodb_table_name

    ddb_client = aws_session(table_region).client('dynamodb')
    print("Checking if table exists...")
    tableExists = True
    try:
        ddb_client.describe_table(TableName=table_name)
        tableExists = True
    except ClientError as e:
        exception = e.response.get('Error').get('Code')
        if exception == 'ResourceNotFoundException':
            tableExists = False

    if tableExists:
        print("Table '{name}' already exists.".format(
            name=table_name))
        sys.exit(1)

    table = aws_session(table_region).resource('dynamodb').create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'resource_id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'tag_key',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'proposer',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'resource_type',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'resource_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'tag_key',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        },
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'proposer-resource_type',
                'KeySchema': [
                    {
                        'AttributeName': 'proposer',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'resource_type',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ]
    )
    while table.table_status == 'CREATING':
        print("Table '{name}' is '{status}'...".format(
            status=table.table_status,
            name=table_name
        ))
        time.sleep(5)
        table.reload()

    print("Table '{arn}' has status '{status}'".format(
        arn=table.table_arn,
        status=table.table_status
    ))


if __name__ == '__main__':
    run()
