import boto3
import time

def create_key_pair(ec2, name):
    key_pair = ec2.create_key_pair(KeyName=name)
    
    # Save the private key to a .pem file
    with open(f'./{name}.pem', 'w') as file:
        file.write(key_pair['KeyMaterial'])

def create_security_group(ec2, vpc_id, my_ip):
    sg = ec2.create_security_group(
        GroupName='autogpt_sg',
        Description='autogpt security group',
        VpcId=vpc_id
    )

    sg_id = sg['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': my_ip}]
            }
        ]
    )

    return sg_id

def create_instance(ec2, sg_id, subnet_id):
    instances = ec2.run_instances(
        ImageId='ami-0d031739ffd848d36', # replace with your AMI ID
        MinCount=1,
        MaxCount=1,
        InstanceType='t3a.large',
        KeyName='autogpt',
        NetworkInterfaces=[{
            'SubnetId': subnet_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [sg_id]
        }]
    )

    return instances['Instances'][0]['InstanceId']

def main():
    ec2 = boto3.client('ec2', region_name='us-east-1')
    create_key_pair(ec2, 'autogpt')
    sg_id = create_security_group(ec2, 'vpc-0586f98caaf989e08', '73.134.197.241/32')
    instance_id = create_instance(ec2, sg_id, 'subnet-0a2dc906b0546ff4a')

    print('Created instance with ID:', instance_id)

if __name__ == '__main__':
    main()

