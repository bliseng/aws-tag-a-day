# aws-tag-a-day
A tool for simplifying swarming of fixing tags

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

## Extending
`aws-tag-a-day` is built on a plugin architecture, using `entry_point` in [`setuptools`](https://setuptools.readthedocs.io/en/latest/setuptools.html).
