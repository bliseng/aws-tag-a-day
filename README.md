# aws-tag-a-day
A tool for simplifying multiple people fixing tags by proposing a tag a day for resources with those missing tags.

[![Build Status](https://travis-ci.com/bliseng/aws-tag-a-day.svg?branch=master)](https://travis-ci.com/bliseng/aws-tag-a-day)
[![PyPI version](https://badge.fury.io/py/aws-tag-a-day.svg)](https://badge.fury.io/py/aws-tag-a-day)

## Installation

```bash
pip install aws-tag-a-day
```

## Quickstart

```bash
# Generate configuration file
mkdir -p ~/.config/tagaday/
cat > ~/.config/tagaday/config.yml <<EOY
dynamodb-table-name: 'tag-proposals'
dynamodb-table-region: 'eu-west-2'
services:
- rds
- ec2
- s3
- emr
regions:
- us-east-1
required-tags:
- Project
- Owner
- Name
- Service
- Availability
EOY

# Create dynamodb table defined in the above config file.
# If the table exists already, the utility will not overwrite it.
tag-a-day-initialise

# Start proposing tags
tag-a-day

```

## Motivation
There are a lot of tools for handling batch tagging, but not many tools for aiding in filling in empty tags on a large scale.

The suggested workflow is:

1. Create configuration file.
2. Create a DynamoDB table by running `tag-a-day-initialise`. This is not a destructive operation, and existing tables will not be modified or removed. The utility will throw an error if the table already exists.
3. Have 1 or more people start using `tag-a-day`.
4. Reconcile any divergent or duplicate tags by running `tag-a-day-reconcile`, and discuss any duplicate tagging suggestions.
5. Apply the tags to the resources.

__NOTE__: Steps 4 and 5 are not yet implemented by this utility.

## Reference

### Supported Services

 - [emr](./tag_a_day/services/emr.py)
 - [ec2](./tag_a_day/services/ec2.py)
 - [s3](./tag_a_day/services/s3.py)
 - [rds](./tag_a_day/services/rds.py)

### Configuration File & CLI options

| Configuration File Key   | Type   | CLI Option                | Type                   | Description                                                                                                                                                                      |
|--------------------------|--------|---------------------------|------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `regions:`               | List   | `--regions`               | Comma separated string | List of regions to audit resources in                                                                                                                                            |
| `services:`              | List   | `--services`              | Comma separated string | List of services to audit                                                                                                                                                        |
| `required-tags:`         | List   | `--required-tags`         | Comma separated string | List of tags which must be present on all resources                                                                                                                              |
| `dynamodb-table-name:`   | String | `--dynamodb-table-name`   | String                 | Name of the DynamoDB table to propose tags to. If used in conjunction with `tag-a-day-initialise`, this will be the DynamoDB table to be created.                                |
| `dynamodb-table-region:` | String | `--dynamodb-table-region` | String                 | AWS Region in which to look for `--dynamodb-table-name`. If used in conjunction with `tag-a-day-initialise` this will be the region which the DynamoDB table will be created in. |
|                          |        | `--resource-ids`          | Comma separated string | List of resource ids, to filter only for specific resources to propose tags for.                                                                                                 |

## Extending
`aws-tag-a-day` is built on a plugin architecture, using `entry_point` in [`setuptools`](https://setuptools.readthedocs.io/en/latest/setuptools.html).

To add more TagHandlers, you can either add classes to this repo, or create a new python package with its
own setup.py, and hook into the plugin architecture using the `tag_a_day.tag_handlers` entrypoint.

1. Create a new class, inheriting from `tag_a_day.services.service.Service`
   ```python
   from tag_a_day.services.service import Service
   
   class CustomTagHandler(Service): pass
   ```

2. Set a unique name for the Tag handler
   ```python
   from tag_a_day.services.service import Service
   
   class CustomTagHandler(Service):
      name='custom_handler'
   ```

3. Create two stub methods, `resources` and `handler` matching the signatures below:
   ```python
   from tag_a_day.services.service import Service
    
   class VpcTagHandler(Service):
      name='ec2_vpc'
   
      def resources(self, session):
        pass
   
      def handler(self, resource, expected_tags, region, session, cache, proposals):
        pass
   ```

4. Implement `resources(...)` to return an iterable. If using boto3 resources,
this should look like:
   ```python
     def resources(self, session):
       return session.resource('ec2').vpc.all()
   ```
   If using boto3 client, don't forget to implement pagination, and should look like:
   ```python
     def resources(self, session):
       ec2 = session.client('ec2')
       paginator = ec2.get_paginator('describe_vpcs')
    
       for page in paginator.paginate():
         for vpc in page:
           yield vpc 
   ```
   
5. Implement `handle(...)` to yield a payload describing the tag proposal (example is using boto3.resources):
    ```python
      def handle(self, vpc, expected_tags, region, session, cache, proposals):
        # This boilerplate logic will handle checking the tags which have already been
        # evaluated for this user.
        evaluated_tags = self._progress.evaluated_tags(vpc.vpc_id)
        vpc_info, missing_tags = \
            self._build_tag_sets(expected_tags, evaluated_tags, vpc.tags)

        # Check if the user has proposed values for all the missing tags 
        if self._progress.has_finished(vpc.vpc_id, expected_tags):
            # Print a skip message
            self._skip(vpc.vpc_id)
            return
         
        if any(missing_tags):
          # Print information about this resource, which could be useful 
          # to provide context around tagging.
          self._print_table(
            ("VpcID", vpc.vpc_id),
            *vpc_info
          )

          # Allow the user to skip auditing this resource       
          if self._user_skip():
            return

          # Build our user prompt to ask for new tags
          tag_prompt = self._build_tag_prompt(missing_tags)
          for tag_key in missing_tags:
            # Yield a proposal for a new tag key/value pair for the given
            # resource id.
            yield {
              'resource_id': vpc.vpc_id,
              'tag_key': tag_key,
              'tag_value': tag_prompt(tag_key),
            }
    ```
    
6. Finally, add the entrypoint by extending `setup.py`:
    ```python
    from setuptools import setup

    setup(
      ...,
      entry_points={
        'tag_a_day.tag_handlers': [
          'vpc = my_package.my_module:VPCTagHandler',
        ],
      }
    )
 

```