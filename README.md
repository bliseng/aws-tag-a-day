# aws-tag-a-day
A tool for simplifying swarming of fixing tags

[![Build Status](https://travis-ci.com/bliseng/aws-tag-a-day.svg?branch=master)](https://travis-ci.com/bliseng/aws-tag-a-day)

## Installation

```bash
pip install aws-tag-a-day
```

## Quickstart

```bash

```

## Motivation
There are a lot of tools for handling batch tagging, but not many tools for aiding in filling in empty tags on a large scale.

## Extending
`aws-tag-a-day` is built on a plugin architecture, using `entry_point` in [`setuptools`](https://setuptools.readthedocs.io/en/latest/setuptools.html).
