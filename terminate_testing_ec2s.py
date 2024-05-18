import boto3

ec2 = boto3.client('ec2')

filters = [
    {
        'Name': 'tag:Name',
        'Values': ['testing*']
    },
    {
        'Name': 'instance-state-name', 
        'Values': ['running']
    }
]

response = ec2.describe_instances(Filters=filters)

instances = []
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        instances.append(instance['InstanceId'])

print(f"Instances to be terminated: {instances}")

# Uncomment the following line to terminate the instances
ec2.terminate_instances(InstanceIds=instances)

