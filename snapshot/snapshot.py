#!/usr/local/bin/python3
import sys
import boto3
import click
import botocore

session = boto3.Session(profile_name='default',region_name='us-east-1')
ec2 = session.resource('ec2')

def filter_instances(project):
    if project:
        filters = [{'Name':'tag:project','Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

@click.group()
def cli():
    """ snapshot.py manages snapshots """

@cli.group("snapshots")
def snapshots():
    """ Commands for Snapshots """

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")

@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume, not just most recent")

def list_snapshots(project, list_all):
    "List EC2 Snapshots: "
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(",".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break
    return

@cli.group('volumes')
def volumes():
    """ Commands for volumes """

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")

def list_volumes(project):
    "List EC2 Volumes: "
    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(",".join((
            v.id,
            i.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))

@cli.group('instances')
def instances():
    """ Commands for instances"""

@instances.command('snapshot',
    help="Create snapshots of all volumes")

@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

def create_snapshots(project):
    """ Create Snapshots for EC2 instances """

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print(" Skipping {0}, snapshot already in progress".format(v.id))
                continue
            print("  Creating Snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Snapshot Analyzer")
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()
    print("Job's done !!!")
    return

@instances.command('list')
@click.option('--project', default=None, 
    help="Only instances for project (tag Project:<name>)")

def list_instances(project):
    "List EC2 Instances : "
    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        #print(i.id,i.instance_type,i.key_name,i.state['Name'],i.placement['AvailabilityZone'])
        print(','.join((
              i.id,
              i.instance_type,
              i.placement['AvailabilityZone'],
              i.state['Name'],
              tags.get('project','<no project>'))))

@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project")

def stop_instances(project):
    "Stop EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botcore.exceptions.ClientError as e:
            print(" Could not stop {0}..".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project")

def start_instances(project):
    "Start EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botcore.exceptions.ClientError as e:
            print(" Could not start {0}..".format(i.id) + str(e))
            continue

    return

if __name__ == "__main__":
   cli()


#s3  = session.resource('s3')
#for i in s3.buckets.all():
#    print(i)

