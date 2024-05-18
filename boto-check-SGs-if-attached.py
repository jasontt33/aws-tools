#!/usr/bin/env python3
import boto3

ec2 = boto3.client('ec2')

# Get a list of all security groups
security_groups = ec2.describe_security_groups()['SecurityGroups']
count = 0
# Iterate over each security group and check if it is in use
for sg in security_groups:
    # Get a list of all network interfaces associated with the security group
    network_interfaces = ec2.describe_network_interfaces(Filters=[
        {'Name': 'group-id', 'Values': [sg['GroupId']]}
    ])['NetworkInterfaces']

    
    # If there are no network interfaces associated with the security group, delete it
    if not network_interfaces:
        count+=1
        print("")
        print(f" security group {sg['GroupId']} is not in use. want to delete it?")
        response = ec2.describe_security_groups(GroupIds=[sg['GroupId']])
        #print(response)
        print("")
        print("Name of Group: " +response.get('SecurityGroups')[0].get('GroupName'))
        print("")
        print("Describe IpPermissions: " + str(response.get('SecurityGroups')[0].get('IpPermissions')))
#        prompt = input("Do you want to delete this SG? (y/n): ")
#        if prompt == "y":
#            print("Deleting security group " + sg['GroupId'])
#            ec2.delete_security_group(GroupId=sg['GroupId'])
#        else:
#            print("Skipping security group " + sg['GroupId'])
            
print("Total count for all SGs not attached ",count)
