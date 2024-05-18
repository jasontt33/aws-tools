#!/usr/bin/env python3
import boto3

ec2 = boto3.client('ec2')

instances = ec2.describe_instances()

resources_without_tags = []

# iterate over instances and print all tags
for reservation in instances['Reservations']:
    for instance in reservation['Instances']:
        instance_id = instance['InstanceId']
        tags = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [instance_id]}])
        print(f'Tags for instance {instance_id}:')
        for tag in tags['Tags']:
            print(f"{tag['Key']}: {tag['Value']}")