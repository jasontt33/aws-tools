import boto3
from botocore.exceptions import ClientError
import argparse

cw_client = boto3.client('cloudwatch')
sns_client = boto3.client('sns')

def main():
    # Define the argument parser
    parser = argparse.ArgumentParser(description='This script will add alarms to an EC2 instance, and send an email when the alarm is triggered. Please provide the instance ID as an argument.')
    parser.add_argument('arg', type=str, help='The instance ID of the EC2 instance you want to add alarms to. Example: python3 create_alarms_for_ec2.py i-0a1b2c3d4e5f6g7h8')

    # Add an optional help menu
    #parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        #help='Run this script like this to add alarms to an EC2 instance: python3 create_alarms_for_ec2.py i-0a1b2c3d4e5f6g7h8')

    # Parse the arguments
    args = parser.parse_args()
    instance_id = args.arg
    # Print the argument value
    print(args.arg)
    return instance_id


# Create an SNS topic
def create_sns_topic(instance_id):
    topic_arn_cpu = sns_client.create_topic(Name='CPU_Utilization_'+instance_id)['TopicArn']
    sns_client.subscribe(
        TopicArn=topic_arn_cpu,
        Protocol='email',
        Endpoint='customsolutions@example.org'
    )

    topic_arn_memory = sns_client.create_topic(Name='Memory_Use_'+instance_id)['TopicArn']
    sns_client.subscribe(
        TopicArn=topic_arn_memory,
        Protocol='email',
        Endpoint='customsolutions@example.org'
    )

    topic_arn_disk_use = sns_client.create_topic(Name='Disk_utilization_'+ instance_id)['TopicArn']
    sns_client.subscribe(
        TopicArn=topic_arn_disk_use,
        Protocol='email',
        Endpoint='customsolutions@example.org'
    )
    return topic_arn_cpu, topic_arn_memory, topic_arn_disk_use

def create_cloudwatch_alarm(instance_id, topic_arn_cpu, topic_arn_memory, topic_arn_disk_use):
    # Create an alarm for CPU utilization
    try:
        response = cw_client.put_metric_alarm(
            AlarmName='CPUUtilization '+instance_id,
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='CPUUtilization',
            Namespace='AWS/EC2',
            Period=60,
            Statistic='Average',
            Threshold=80.0,
            ActionsEnabled=True,
            AlarmActions=[topic_arn_cpu],
            AlarmDescription='Alarm when CPU exceeds 80%',
    )
        print(f'Created alarm {response}')
    except ClientError as e:
        print(f'Error creating alarm: {e}')

    # Set up the dimensions for the disk utilization alarm
    dimensions = [
        {'Name': 'InstanceId', 'Value': instance_id},
        # monitor the root volume
        {'Name': 'Filesystem', 'Value': '/dev/xvda1'}
    ]

    # Create an alarm for disk utilization
    try:
        response = cw_client.put_metric_alarm(
            AlarmName='DiskUtilizationOver90 '+instance_id,
            MetricName='DiskSpaceUtilization',
            Namespace='AWS/EC2',
            Dimensions=dimensions,
            Statistic='Average',
            ComparisonOperator='GreaterThanThreshold',
            Period=60,
            Threshold=90.0,
            EvaluationPeriods=1,
            AlarmDescription='Alarm when disk utilization exceeds 90%',
            ActionsEnabled=True,
            AlarmActions=[topic_arn_disk_use]
        )
        print(f'Created alarm {response}')
    except ClientError as e:
        print(f'Error creating alarm: {e}')

    print(f'Created alarm {response}')

    # Create an alarm for memory utilization
    try:
        response = cw_client.put_metric_alarm(
            AlarmName='MemoryUtilization '+instance_id,
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=1,
            MetricName='MemoryUtilization',
            Namespace='AWS/EC2',
            Period=60,
            Statistic='Average',
            Threshold=90.0,
            ActionsEnabled=True,
            AlarmDescription='Alarm when server Memory exceeds 90%',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },
            ],
            Unit='Percent',
            AlarmActions=[topic_arn_memory]
        )
        print(f'Created alarm {response}')
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceExists':
            print('Alarm already exists')
        else:
            print('Error creating alarm: ', e)



if __name__ == '__main__':
    instance_id = main()
    topic_arn_cpu, topic_arn_memory, topic_arn_disk_use = create_sns_topic(instance_id)
    create_cloudwatch_alarm(instance_id, topic_arn_cpu, topic_arn_memory, topic_arn_disk_use)

