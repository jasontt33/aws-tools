import boto3

# Create a session object for profile1
session_profile1 = boto3.Session(profile_name='default')

# Create a session object for profile2
session_profile2 = boto3.Session(profile_name='stf')


# Initialize Boto3 EC2 client
ec2 = session_profile1.client("ec2", region_name='us-east-1')
ec2_stf = session_profile2.client("ec2", region_name='us-east-1')

# Get a list of EC2 instances
response = ec2.describe_instances()

instances = []
for reservation in response["Reservations"]:
    instances.extend(reservation["Instances"])

# Function to get instance name from tags
def get_instance_name(instance):
    for tag in instance.get("Tags", []):
        if tag["Key"] == "Name":
            return tag["Value"]
    return None

# Create an SSH config file
with open("config", "w") as ssh_config:
    for instance in instances:
        name = get_instance_name(instance)
        if name and instance.get("KeyName") and instance.get("PublicIpAddress"):
            ssh_config.write(f"Host {name}\n")
            ssh_config.write(f"  HostName {instance['PublicIpAddress']}\n")
            ssh_config.write(f"  User ec2-user\n") # Replace 'ec2-user' with the appropriate user if needed
            ssh_config.write(f"  Port 22\n")
            ssh_config.write(f"  IdentityFile ~/example/{instance['KeyName']}.pem\n")
            ssh_config.write("\n")

# Get a list of EC2 instances
response2 = ec2_stf.describe_instances()

instances = []
for reservation in response2["Reservations"]:
    instances.extend(reservation["Instances"])

# Function to get instance name from tags
def get_instance_name(instance):
    for tag in instance.get("Tags", []):
        if tag["Key"] == "Name":
            return tag["Value"]
    return None

# Add to an SSH config file STF values
with open("config", "a") as ssh_config:
    for instance in instances:
        name = get_instance_name(instance)
        if name and instance.get("KeyName") and instance.get("PublicIpAddress"):
            ssh_config.write(f"Host {name}\n")
            ssh_config.write(f"  HostName {instance['PublicIpAddress']}\n")
            ssh_config.write(f"  User ec2-user\n") # Replace 'ec2-user' with the appropriate user if needed
            ssh_config.write(f"  Port 22\n")
            ssh_config.write(f"  IdentityFile ~/example/{instance['KeyName']}.pem\n")
            ssh_config.write("\n")

print("SSH config file created.")
