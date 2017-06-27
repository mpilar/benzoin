"""
Validates all mongodb collections and tags snapshots from config file.
"""
from os import environ as env
from time import sleep
import argparse
import json
import boto3
import botocore.vendored.requests as requests

import pymongo


VALIDATION_TAG_KEY = env.get("VALIDATION_TAG_KEY",
                             "Validated")

class ValidationFailed(Exception):
    """ A typed error indicating the process is not done """
    pass

def validate_all_collections():
    """ Connecto to mongo and run db.collection.validate() on everything """
    retry_count = 0
    try:
        client = pymongo.MongoClient("localhost", 27017, maxPoolSize=50)
    except Exception as exc:
        if retry_count > 20:
            raise Exception("Retries exceeded") from exc
        retry_count += 1
        sleep(6)
    for db in (client[name] for name in
               client.database_names()
               if name != "local"):
        for collection in db.collection_names(include_system_collections=False):
            if db.validate_collection(collection, scandata=True, full=True)['errors']:
                raise ValidationFailed("Collection failed to validate", collection)


def update_tags(region, snapshot_ids, success):
    """Check and update the tags in the snapshot."""
    session = boto3.session.Session(region_name=region)
    ec2 = session.resource('ec2')
    
    for sid in snapshot_ids:
        snapshot = ec2.Snapshot(sid)
        current_tags = snapshot.tags
        if not current_tags:
            current_tags = []
        current_tags.append({"Key": VALIDATION_TAG_KEY, "Value": str(success).lower()})
        snapshot.create_tags(Tags=current_tags)

def are_snapshots_tagged(region, snapshot_ids):
    """Check the current snapshot tags to prevent multiple snapshots."""
    session = boto3.session.Session(region_name=region)
    ec2 = session.resource('ec2')
    
    for sid in snapshot_ids:
        snapshot = ec2.Snapshot(sid)
        current_tags = snapshot.tags
        if not current_tags:
            continue
        for tag in current_tags:
            if tag.get("Key") == VALIDATION_TAG_KEY:
                return True
    return False


def main():
    """
    Parse arguments and trigger main application
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="The region to operate in.", default="us-east-1")
    parser.add_argument("jsondoc", help="The json document describing the snapshot.")
    args = parser.parse_args()
    config = {}
    with open(args.jsondoc, 'r') as jsonf:
        config = json.load(jsonf)
    snapshot_ids = [vol["snapshot-id"] for vol in config.get("backup-volumes")]
    region = config["region"]
    try:
        if are_snapshots_tagged(region, snapshot_ids):
            return
        validate_all_collections()
        update_tags(region, snapshot_ids, True)
    except Exception as exc:
        update_tags(region, snapshot_ids, False)
        #TODO: Add alerting, monitoring, chaos, destruction, etc.
        raise exc


if __name__ == "__main__":
    main()

