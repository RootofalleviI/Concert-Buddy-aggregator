"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws

# Create a new security group for our server to allow HTTP and SSH access
security_group = aws.ec2.SecurityGroup(
    'concert-buddy',
    description='Allow all traffic',
    ingress=[
        {'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0']}
    ],
    egress=[
        {'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0']}
    ]
)

# Find the latest Ubuntu AMI in the given region
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical
    filters=[{"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]}])

script = """#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# Update and install necessary packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip git
"""

# Create a new EC2 instance
instance = aws.ec2.Instance(
    'fastapi-instance',
    instance_type='t2.micro',  # Update to the instance type you need
    security_groups=[security_group.name],
    ami=ami.id,
    user_data=script)

# Export the public IP of the instance
pulumi.export('publicIp', instance.public_ip)
pulumi.export('publicHostName', instance.public_dns)
