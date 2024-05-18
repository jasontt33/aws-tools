#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
import json
import sys
import argparse

client = boto3.client('cognito-idp')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pool_name", help="Name of the user pool")
    parser.add_argument("auto_verified_attributes", help="Attributes to auto verify, e.g. 'email'")
    parser.add_argument("owner", help="Owner of the user pool, e.g. 'John Doe'")

    args = parser.parse_args()
    create_user_pool(args.pool_name, args.auto_verified_attributes)

def create_user_pool(pool_name, auto_verified_attributes):
    try:
        # Create a user pool
        response = client.create_user_pool(
            PoolName=pool_name,
            AutoVerifiedAttributes=[auto_verified_attributes],
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 12,
                    'RequireLowercase': True,
                    'RequireUppercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': True,
                    'TemporaryPasswordValidityDays': 7
                }
            },
            UsernameAttributes=[auto_verified_attributes],
            EmailVerificationSubject='Verify your email for this user pool' + pool_name,
            EmailVerificationMessage='Please click the link below to verify your email: {####}',
            SmsVerificationMessage='Your verification code is {####}'
        )
        print(response)
        user_pool_id = response['UserPool']['Id']
        return user_pool_id
    except ClientError as e:
        print(e.response['Error']['Message'])

def add_tags_to_user_pool(user_pool_id, owner):
    region = 'us-east-1'
    account_id = '955254544426'

    # Add tags to user pool
    client.tag_resource(
        ResourceArn=f'arn:aws:cognito-idp:'+region+':'+account_id+':userpool/{user_pool_id}',
        Tags=[
            {
                'Key': 'Owner',
                'Value': owner
            }
        ]
    )
    

if __name__ == "__main__":
    main()
