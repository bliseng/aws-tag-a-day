import os

import hconf


class Configuration(hconf.ConfigManager):
    DEFAULT_SERVICES = ['ec2', 's3', 'rds']

    def process_list(self, data):
        if type(data) == list:
            return data
        return data.split(',')

    def __init__(self, session):
        self._session = session
        super().__init__(
            {'name': 'regions', 'default': [],
             'required': False, 'cast': self.process_list,
             'description': 'List of regions to check tags in'},
            {'name': 'services', 'default': [],
             'required': False, 'cast': self.process_list,
             'description': 'List of Services to check tags on'},
            {'name': 'required-tags',
             'required': True, 'cast': self.process_list,
             'description': 'List of tags which must exist'},
            {'name': 'dynamodb-table-name',
             'required': True,
             'description': 'Name of DynamoDB table to write tagging proposals to'},
            {'name': 'dynamodb-table-region',
             'required': True,
             'description': 'Region the DynamoDB table exists in'},
        )

        self.registerParser(hconf.Subparsers.YAML(
            filename="config.yml", filepath=os.path.expanduser('~/.config/tagaday/')
        ))

        self.registerParser(hconf.Subparsers.Cmdline(
            'Tool to work through AWS and tag instances')
        )

    def parse(self):
        cfg = super().parse()
        self._process_defaults(cfg)
        return cfg

    def _process_defaults(self, cfg):
        if len(cfg.regions) == 0:
            cfg.regions = [region['RegionName'] for region in
                           self._session().client('ec2').describe_regions()['Regions']]
