#!/usr/bin/env python3
"""
Self snapshotting script
"""
import json
import argparse
from pprint import pprint
from os import environ as env
from uuid import uuid4
import boto3

STATE_MACHINE_ARN = env.get("STATE_MACHINE_ARN",
                            "arn:aws:states:us-east-1:201973737062:stateMachine:BENZOIN")


def perform_backup(region, instance_id):
    """
    Find intance's Block Devices to find the volumes that need to be backed up.
    After the snapshots are triggered start a step function to verify the,
    """
    session = boto3.session.Session(region_name=region)
    client = session.client('ec2')
    instance_data = client.describe_instances(InstanceIds=[instance_id])
    reservation = instance_data.get('Reservations')[0]
    block_mappings = reservation.get('Instances')[0].get('BlockDeviceMappings')

    volume_ids = []

    for mapping in block_mappings:
        if 'Ebs' in mapping and mapping.get('DeviceName') != '/dev/sda1':
            volume_ids.append(mapping.get('Ebs').get('VolumeId'))

    volume_descriptions = client.describe_volumes(VolumeIds=volume_ids).get('Volumes')


    backup_volumes = []
    for description in volume_descriptions:
        tags = description.get('Tags')
        if any(tag['Key'] == 'AllowSelfBackup' for tag in tags):
            device = description.get('Attachments', [{}])[0].get('Device', '/dev/sdb')
            backup_volumes.append({'device':device, 'volume-id':description.get('VolumeId')})


    for volume in backup_volumes:
        snap = client.create_snapshot(Description="Benzoin created backup",
                                      VolumeId=volume.get('volume-id'))
        volume['snapshot-id'] = snap.get('SnapshotId')

    snapshot_dict = {
        "backup-volumes": backup_volumes,
        "region": region
    }
    sfn_client = session.client('stepfunctions')
    sfn_client.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=str(uuid4()),
        input=json.dumps(snapshot_dict)
    )



def main():
    """
    Parse arguments and trigger main application
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="The region to operate in.", default="us-east-1")
    parser.add_argument("instance_id",
                        help="The instance-id to backup. For testing: i-0e40ba9e87ea519d0")
    args = parser.parse_args()
    print(args)
    try:
        perform_backup(args.region, args.instance_id)
    except Exception as exc:
        #TODO: Add alerting, monitoring, chaos, destruction, etc.
        raise exc


if __name__ == "__main__":
    main()


