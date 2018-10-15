from boto3 import Session

from tag_a_day.cache import AWSCache
from tag_a_day.config import Configuration
from tag_a_day.log import logger
from tag_a_day.services import Services


def run():
    def aws_session(region='us-east-1'):
        return Session(region_name=region)

    conf = Configuration(aws_session).parse()
    cache = AWSCache(aws_session)

    table = aws_session(). \
        resource('dynamodb', conf.dynamodb_table_region). \
        Table(conf.dynamodb_table_name)
    services = Services(
        session=aws_session,
        cache=cache,
        services=conf.services,
        proposals=table)

    for region in conf.regions:
        session = aws_session(region)
        for service in services:
            logger().info(
                'Auditing tags for {0} in {1}'.format(service, region))
            service.run(
                expected_tags=conf.required_tags,
                region=region,
                session=session,
                proposals=table)


if __name__ == '__main__':
    run()
