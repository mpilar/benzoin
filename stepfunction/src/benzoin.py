"""
Supporting lambda functions for Benzoin Step Function
"""
from os import environ as env
from json import dumps
import boto3

class NotReady(Exception):
    """ A typed error indicating the process is not done """
    pass

VALIDATION_INSTANCE_TYPE = env.get("VALIDATION_INSTANCE_TYPE",
                                   "t2.micro")
RESTORE_AMI = env.get("RESTORE_AMI",
                      "ami-85d9e893")
RESTORE_SGS = env.get("RESTORE_SGS",
                      "sg-48a41139").split(",")
RESTORE_NET = env.get("RESTORE_SUBNET",
                      "subnet-1905af43")
RESTORE_KEYNAME = env.get("RESTORE_KEYNAME",
                          "exercise")
RESTORE_INSTANCE_PROFILE = env.get("RESTORE_INSTANCE_PROFILE",
                                   "benzoin_restore_instance")
VALIDATION_TAG_KEY = env.get("VALIDATION_TAG_KEY",
                             "Validated")


def initialize_snapshot_tags(event, context):
    """
    Event comes in with snapshot info, make sure we"re working with a snapshot
    we"re supposed to and wait for it to be done snapshotting.
    """
    session = boto3.session.Session(region_name=event.get("region"))

    ec2 = session.resource("ec2")

    snapshot_ids = [vol["snapshot-id"] for vol in event.get("backup-volumes")]
    for sid in snapshot_ids:
        if ec2.Snapshot(sid).state != "completed":
            raise NotReady("Snapshot not ready")

    return event

def create_validation_instance(event, context):
    """
    Create an instance using the restore AMI and the correct snapshot.
    """
    session = boto3.session.Session(region_name=event.get("region"))

    ec2 = session.resource("ec2")
    subnet = ec2.Subnet(RESTORE_NET)
    device_mappings = []

    snapshot_ids = [(vol["snapshot-id"], vol["device"]) for vol in event.get("backup-volumes")]
    for sid, device in snapshot_ids:
        device_mappings.append({
            "DeviceName": device,
            "Ebs": {
                "SnapshotId": sid
            }
        })

    event_json = dumps(event)

    user_data = f"""
{event_json}
"""

    tags = [
        {
            "Key": "Name",
            "Value": "mdb-restore"
        },
        {
            "Key": "AllowSelfBackup",
            "Value": "true"
        },
        {
            "Key": "BenzoinRestoreInstance",
            "Value": "true"
        }
    ]


    instance_args = {
        "ImageId":RESTORE_AMI,
        "InstanceType":VALIDATION_INSTANCE_TYPE,
        "SecurityGroupIds":RESTORE_SGS,
        "UserData":user_data,
        "MinCount":1,
        "MaxCount":1,
        "BlockDeviceMappings":device_mappings,
        "IamInstanceProfile":{
            "Name": RESTORE_INSTANCE_PROFILE
        },
        "TagSpecifications":[
            {
                "ResourceType": "instance",
                "Tags": tags
            },
            {
                "ResourceType": "volume",
                "Tags": tags
            },
        ]
    }
    if RESTORE_KEYNAME:
        instance_args["KeyName"]=RESTORE_KEYNAME
    instance = subnet.create_instances(**instance_args)
    event["instance-id"] = instance[0].instance_id

    return event

def wait_for_snapshot_validation(event, context):
    """
    Gets the snapshots involved in the step function and checks for success
    of the MongoDB validator script.
    """
    session = boto3.session.Session(region_name=event.get("region"))

    ec2 = session.resource("ec2")
    snapshot_ids = [vol["snapshot-id"] for vol in event.get("backup-volumes")]
    for sid in snapshot_ids:
        tags = ec2.Snapshot(sid).tags
        if not tags:
            break
        for tag in tags:
            if tag.get("Key") == VALIDATION_TAG_KEY:
                if tag.get("Success") == "false":
                    raise Exception("Validation failed!")
                else:
                    return event
    raise NotReady("Snapshot not validated yet.")

def apply_retention_policy(event, context):
    """ Apply retention policy """
    # TODO: Come up with a sane backup retention policy and implement it here
    # Keep:
    # Hourlies for X days
    # Dailies for X weeks
    # Weeklies for X months
    # Monthlies for X years
    # NOTE: This requires modification of the snapshot tags so that the retention
    # policy gets applied upon creation.
    return event

def success(event, context):
    """ Handle success messaging """
    # TODO: Notify of success somewhere? Database? Metrics? For now... CloudWatch Logs!
    print(event)
    return event

def error_handler(event, context):
    """ Handle (by notifying) any errors that happen in the step function. """
    # TODO: Notify of error somewhere? Database? Metrics? PagerDuty? CloudWatch Alarm?
    # Also note that CloudWatch can be made to alert on Step Function execution errors
    print(event)
    return event

def terminate_instances(event, context):
    """ Terminate instance identified in the event """
    session = boto3.session.Session(region_name=event.get("region"))

    ec2 = session.resource("ec2")
    ec2.Instance(event["instance-id"]).terminate()
    return event