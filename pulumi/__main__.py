"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws

# Create a new security group for our server to allow HTTP and SSH access
secgroup = aws.ec2.SecurityGroup(
    'fastapi-secgroup',
    description='Allow HTTP and SSH',
    ingress=[
        {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0']},
        {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0']}
    ])

# Find the latest Ubuntu AMI in the given region
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical
    filters=[{"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]}])

# Create a new EC2 instance
instance = aws.ec2.Instance(
    'fastapi-instance',
    instance_type='t2.micro',  # Update to the instance type you need
    security_groups=[secgroup.name],
    ami=ami.id,
    user_data="""#!/bin/bash
        # Your commands to set up the FastAPI environment go here
        # For example, install Python, FastAPI, gunicorn, etc.
        # Clone your FastAPI application repository
        # Start your FastAPI application
    """)

# Export the public IP of the instance
pulumi.export('instance_ip', instance.public_ip)
