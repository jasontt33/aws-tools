import boto3

ec2 = boto3.client('ec2')

response = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])
count = 0

for volume in response['Volumes']:
    if 'Attachments' not in volume or len(volume['Attachments']) == 0:
        count+=1
        print(f"Deleting volume {volume['VolumeId']}")
        ec2.delete_volume(VolumeId=volume['VolumeId'])


print(count,' number of ebs volumes deleted not in use')


