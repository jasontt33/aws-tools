import boto3

ec2 = boto3.client('ec2')

# Get information about all running instances
response = ec2.describe_instances()

count = 0

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        # Skip instances without a public IP address
        if 'PublicIpAddress' not in instance:
            continue

        # Get the instance ID
        instance_id = instance['InstanceId']

        # Get the instance name
        name = ''
        for tag in instance['Tags']:
            if tag['Key'] == 'Name':
                name = tag['Value']
                break

        # Get the key pair name
        key_pair_name = instance.get('KeyName', 'No key pair name')  # Using get() method for safety

        # Get the public IP address
        public_ip = instance['PublicIpAddress']
        count += 1

        # Do something with the information
        print(f"Instance ID: {instance_id}, Instance name: {name}, Key pair name: {key_pair_name}, Public IP: {public_ip}")

print(f"{count} number of servers found in this query")

