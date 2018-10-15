from setuptools import setup, find_packages

setup(
    name='aws-tag-a-day',
    version='0.1.0',
    packages=find_packages(),
    url='',
    license='Apache2',
    author='Drew J. Sonne',
    author_email='',
    description='',
    install_requires=[
        'tabulate',
        'prompt_toolkit ',
        'hconf',
        'pyyaml'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': [
            'tag-a-day = tag_a_day.cli:run'
        ],
        'tag_a_day.tag_handlers': [
            'ec2 = tag_a_day.services.ec2:EC2TagHandler',
            'rds = tag_a_day.services.rds:RDSTagHandler',
            's3 = tag_a_day.services.s3:S3TagHandler',
            'emr = tag_a_day.services.emr:EMRTagHandler',
        ]
    }
)
