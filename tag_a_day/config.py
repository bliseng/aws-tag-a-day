import os

import hconf


class Configuration(hconf.ConfigManager):

    @staticmethod
    def process_list(data):
        if data is None:
            return data
        if type(data) == list:
            return data
        return data.split(',')

    def __init__(self, session):
        self._session = session
        profile_dir = os.path.expanduser(os.path.join('~', '.config', 'tagaday', ''))

        super(Configuration, self).__init__(
            {'name': 'regions', 'default': [],
             'required': False, 'cast': self.process_list,
             'description': 'List of regions to check tags in'},
            {'name': 'services', 'default': [],
             'required': False, 'cast': self.process_list,
             'description': 'List of Services to check tags on'},
            {'name': 'resource-ids',
             'required': False,
             'description': 'Comma separated list of resources to audit tags on'},
            {'name': 'required-tags',
             'required': True, 'cast': self.process_list,
             'description': 'List of tags which must exist'},
            {'name': 'dynamodb-table-name',
             'required': True,
             'description': 'Name of DynamoDB table to write tagging proposals to'},
            {'name': 'dynamodb-table-region',
             'required': True,
             'description': 'Region the DynamoDB table exists in'},
            {'name': 'profile', 'default': 'config.yml',
             'required': False,
             'description': 'Tagging profile to load. This is the filename defined in `--profile-path`. Default: \'config\''},
            {'name': 'profile-path', 'default': profile_dir,
             'required': False,
             'description': 'Path to directory containing the tagging profiles to load. Default: \'' +
                            profile_dir + '\''}
        )

        self.registerParser(hconf.Subparsers.Cmdline(
            'Tool to work through AWS and tag instances'
        ))

        self.registerParser(hconf.Subparsers.YAML(
            filepathConfig='profile_path', filenameConfig='profile',
        ))

    def parse(self):
        cfg = super(Configuration, self).parse()
        self._process_defaults(cfg)
        return cfg

    def _process_defaults(self, cfg):
        if len(cfg.regions) == 0:
            cfg.regions = [region['RegionName'] for region in
                           self._session().client('ec2').describe_regions()['Regions']]
