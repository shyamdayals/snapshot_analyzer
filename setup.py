from setuptools import setup

setup (
    name='snapshot_analyzer',
    version='0.1',
    author='Shyam Hazari',
    author_email="shyamdayals@yahoo.com",
    description="Snapshot Analyzer is a script to manager AWS EC2 snapshots",
    license="GPLv3+",
    packages=['snapshot'],
    url="https://github.com/shyamdayals/snapshot_analyzer",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        snapshot=snapshot.snapshot:cli
    ''',
)
