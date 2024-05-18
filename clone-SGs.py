import boto3

def clone_security_group(src_security_group_id, dst_security_group_name, dst_vpc_id, region_name='us-east-1'):
    ec2 = boto3.resource('ec2', region_name=region_name)
    client = boto3.client('ec2', region_name=region_name)

    # Get the source security group details
    src_security_group = ec2.SecurityGroup(src_security_group_id)
    src_ingress_rules = src_security_group.ip_permissions
    src_egress_rules = src_security_group.ip_permissions_egress
    src_description = src_security_group.description

    # Create a new security group in the specified VPC
    try:
        response = client.create_security_group(
            GroupName=dst_security_group_name,
            Description=src_description,
            VpcId=dst_vpc_id
        )
        dst_security_group_id = response['GroupId']
    except Exception as e:
        print(f"Failed to create new security group: {e}")
        return None

    # Authorize ingress rules for the new security group
    try:
        client.authorize_security_group_ingress(
            GroupId=dst_security_group_id,
            IpPermissions=src_ingress_rules
        )
    except Exception as e:
        print(f"Failed to authorize ingress rules: {e}")
        return None

    # Authorize egress rules for the new security group
    try:
        client.authorize_security_group_egress(
            GroupId=dst_security_group_id,
            IpPermissions=src_egress_rules
        )
    except Exception as e:
        print(f"Failed to authorize egress rules: {e}")
        return None

    print(f"Successfully cloned security group {src_security_group_id} to {dst_security_group_id}")
    return dst_security_group_id

if __name__ == '__main__':
    src_security_group_id = 'sg-04d7f36f2b7e88c33'  # Replace with the ID of your source security group
    dst_security_group_name = 'serraview-sg3'  # Replace with the name of the new security group
    dst_vpc_id = 'vpc-02922db7dc53276c9'  # Replace with the ID of the destination VPC
    region_name = 'us-east-1'  # Replace with your desired AWS region
    clone_security_group(src_security_group_id, dst_security_group_name, dst_vpc_id, region_name)

