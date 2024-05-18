#!/usr/bin/env python3
import boto3
import sys
from botocore.exceptions import ClientError
import argparse

def create_ec2_instance(server_type, owner, server_name):
    # Set the region and credentials
    ec2 = boto3.resource('ec2')

    # Get the VPC ID
    vpc_id = 'vpc-090abe61ae804970e'

    # Create a security group and authorize inbound SSH traffic
    sec_group = ec2.create_security_group(
        GroupName=server_name + "-SG", Description=server_name + "-SG", VpcId=vpc_id)
    sec_group.authorize_ingress(
        # VPN IP address
        CidrIp='209.133.27.66/32',
        Description='VPN IP address',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22
    )
    # roger Ts IP address
    sec_group.authorize_ingress(
        CidrIp='76.100.185.142/32',
        Description='roger Ts IP address',
        IpProtocol='tcp',
        FromPort=22,
        ToPort=22
    )


    # set tag specifications
    tag_specifications = [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': server_name
                },
                {
                    'Key': 'Owner',
                    'Value': owner
                }
            ]
        }
    ]

    # set user data script
    # set the nameserver to Google b/c the default is not working
    user_data_script = """#!/bin/bash
    echo "nameserver 8.8.8.8" | tee /etc/resolv.conf > /dev/null
    """
    # Prevent the resolv.conf file from being modified
    # write protect the resolv.conf file
    user_data_script_two = """#!/bin/bash chattr +i /etc/resolv.conf """
    user_data_memory_check = '''#!/bin/bash
    sudo yum update -y
    sudo yum install -y amazon-cloudwatch-agent

    # Configure the CloudWatch Agent
    sudo tee /etc/amazon/cloudwatch-agent.json > /dev/null <<EOF
    {
        "metrics": {
            "metrics_collected": {
                "mem": {
                    "measurement": [
                        "mem_used_percent"
                    ],
                    "metrics_collection_interval": 60
                },
                "swap": {
                    "measurement": [
                        "swap_used_percent"
                    ],
                    "metrics_collection_interval": 60
                }
            }
        }
    }
    EOF

    # Start the CloudWatch Agent
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/etc/amazon/cloudwatch-agent.json
    '''

    # Launch a t3a.micro instance
    instance = ec2.create_instances(
        ImageId='ami-005f9685cb30f234b',
        InstanceType=server_type,
        MaxCount=1,
        MinCount=1,
        KeyName = 'devo-dev',
        UserData=user_data_script+user_data_script_two + user_data_memory_check,
        TagSpecifications=tag_specifications,
        NetworkInterfaces=[
            {
                'DeviceIndex': 0,
                'SubnetId': 'subnet-07ef73d81b0a3789e',
                'AssociatePublicIpAddress': True,
                'Groups': [sec_group.group_id]
            }
        ]
    )[0]

    # Wait for the instance to be running
    instance.wait_until_running()
    instance_id = instance.instance_id
    instance_name = server_name
   

    # Print the public IP address of the instance
    
    return instance_id, instance_name

def create_cloudwatch_alarm(instance_id, instance_name):
    sns = boto3.client('sns')
    response = sns.create_topic(Name=instance_id +'_'+ instance_name +'-CPU-alarm')
    topic_arn = response['TopicArn']

    sns = boto3.client('sns')
    response = sns.create_topic(Name=instance_id +'_'+ instance_name +'-disk-use-alarm')
    topic_arn_disk = response['TopicArn']

    sns = boto3.client('sns')
    response = sns.create_topic(Name=instance_id +'_'+ instance_name +'-excessive-memory-use-alarm')
    topic_arn_memory = response['TopicArn']

    cloudwatch = boto3.client('cloudwatch')

    metric_filter = {
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Dimensions": [
        {
            "Name": "InstanceId",
            "Value": instance_id
        }
    ],
    "Period": 60,
    "Stat": "Average"
    }

    alarm_name = instance_id + '_' + instance_name + '_CPU Utilization'
    alarm_description = instance_id + '_' + instance_name + '_CPU Utilization'
    alarm_threshold = 90.0
    alarm_actions = [topic_arn]

    try:
        response_cloudwatch = cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=alarm_description,
            ActionsEnabled=True,
            OKActions=[],
            AlarmActions=alarm_actions,
            MetricName=metric_filter['MetricName'],
            Namespace=metric_filter['Namespace'],
            Statistic=metric_filter['Stat'],
            Dimensions=metric_filter['Dimensions'],
            Period=metric_filter['Period'],
            EvaluationPeriods=1,
            Threshold=alarm_threshold,
            ComparisonOperator='GreaterThanThreshold'
    )
    except ClientError as e:
        print(e)
        print(response_cloudwatch)

    
    metric_filter = {
    "Namespace": "CWAgent",
    "MetricName": "disk_used_percent",
    "Dimensions": [
        {
            "Name": "InstanceId",
            "Value": instance_id
        }
    ]
    }


    alarm_actions_disk = [topic_arn_disk]
    alarm_name = instance_id + ' ' + instance_name + ' Disk Space Utilization'
    alarm_description = instance_id + ' ' + instance_name + ' Disk Space Utilization'
    
    response = cloudwatch.put_metric_alarm(
    AlarmName=alarm_name,
    AlarmDescription=alarm_description,
    ActionsEnabled=True,
    OKActions=[],
    AlarmActions=alarm_actions_disk,
    MetricName='disk_used_percent',
    Namespace='CWAgent',
    Statistic='Average',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': instance_id
        }
    ],
    Period=300,
    EvaluationPeriods=1,
    Threshold=90.0,
    ComparisonOperator='GreaterThanThreshold'
    )

   
    return topic_arn, topic_arn_disk, topic_arn_memory

def subscribe_to_alarm(topic_arn, topic_arn_disk, topic_arn_memory):

    sns = boto3.client('sns')

    response = sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email', # or 'sms'
        Endpoint='customsolutions@example.org' # or your phone number
    )

    response = sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email', # or 'sms'
        Endpoint='smotlani@example.org' # or your phone number
    )

    response = sns.subscribe(
        TopicArn=topic_arn_disk,
        Protocol='email', # or 'sms'
        Endpoint='customsolutions@example.org' # or your phone number
    )

    response = sns.subscribe(
        TopicArn=topic_arn_disk,
        Protocol='email', # or 'sms'
        Endpoint='smotlani@example.org' # or your phone number
    )

    response = sns.subscribe(
        TopicArn=topic_arn_memory,
        Protocol='email', # or 'sms'
        Endpoint='customsolutions@example.org' # or your phone number
    )

    response = sns.subscribe(
        TopicArn=topic_arn_memory,
        Protocol='email', # or 'sms'
        Endpoint='smotlani@example.org' # or your phone number
    )


def main():
    # create argument parser
    parser = argparse.ArgumentParser(description='Build EC2 instance and Cloudwatch alarm. This script takes 3 arguemnts, server type, owner, and server name, in that order. Example: python3 create_ec2_instance.py t3a.micro owner server_name')
    # parse arguments
    args = parser.parse_args()
    print(args)
    # The first argument (index 0) is the name of the script itself
    # create argument parser
    if len(sys.argv) == 4:
        server_type = sys.argv[1]
        owner = sys.argv[2]
        server_name = sys.argv[3]
        # at least one command line argument was passed
        argument = sys.argv[3]
        # do something with the argument
        print("Server Type:", server_type)
        print("Owner:", owner)
        print("Server Name:", server_name)
        instance_id, instance_name = create_ec2_instance(server_type, owner, server_name)
        topic_arn, topic_arn_two = create_cloudwatch_alarm(instance_id, instance_name)
        subscribe_to_alarm(topic_arn, topic_arn_two)
        print('Public IP address of server:', instance_id.public_ip_address)
        
    elif len(sys.argv) == 2 or len(sys.argv) == 1 or len(sys.argv) > 3:
        # no command line arguments were passed
        print("Please provide THREE arguments, 1. server type, e.g. t3a.micro and 2. owner or person creating this VM, e.g. roger Thompson, 3. add a server name, e.g. devo-test-server.")

if __name__ == "__main__":
    main()