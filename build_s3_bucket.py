#!/usr/bin/env python3
import boto3
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='A build S3 bucket script that takes two arguments, 1. for the bucket name and 2. for the owner')
    parser.add_argument('arg1', help='Bucket Name, i.e what do you want to name the bucket')
    parser.add_argument('arg2', help='Owner, i.e who is the owner of the bucket')
    args = parser.parse_args()

    if len(sys.argv) != 3:
        parser.print_help()
        sys.exit(1) # exit with error
    elif len(sys.argv) == 3:
        bucket_name = sys.argv[1]
        owner = sys.argv[2]
        print("Bucket Name:", bucket_name)
        print("Owner:", owner)
        create_bucket(bucket_name, owner)

def create_bucket(bucket_name, owner):
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Define bucket name and tags
    bucket_name = bucket_name
    owner_tag = {'Key': 'Owner', 'Value': owner}
    environment_tag = {'Key': 'Environment', 'Value': 'non-prod'}

    # Create the bucket
    session = boto3.session.Session()
    current_region = session.region_name
    if current_region == 'us-east-1':
        try:
            response = s3.create_bucket(Bucket=bucket_name)
            print(response)
            print('Bucket created in us-east-1' + bucket_name)
        except Exception as error:
            print(error)
    else:
        try:
            response = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': current_region})
            print(response)
            print('Bucket created in ' + current_region + ' ' + bucket_name)
        except Exception as error:
            print(error)
    # Add the tags to the bucket
    s3.put_bucket_tagging(
    Bucket=bucket_name,
    Tagging={'TagSet': [owner_tag, environment_tag]}
    )
    # set the bucket to private
    response_public = s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
    )



if __name__ == '__main__':
    main()