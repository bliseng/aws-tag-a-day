# aws-tag-a-day
A tool for simplifying multiple people fixing tags by proposing a tag a day for resources with those missing tags.

[![Build Status](https://travis-ci.com/bliseng/aws-tag-a-day.svg?branch=master)](https://travis-ci.com/bliseng/aws-tag-a-day)

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
dynamodb-table-region: 'us-east-1'
services:
- rds
- ec2
- s3
regions:
- us-east-1
required-tags:
- Project
- Owner
- Name
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

### Configuration File

### CLI options

## Extending
`aws-tag-a-day` is built on a plugin architecture, using `entry_point` in [`setuptools`](https://setuptools.readthedocs.io/en/latest/setuptools.html).
