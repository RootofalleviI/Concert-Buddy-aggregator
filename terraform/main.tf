# Define the AWS provider and region
provider "aws" {
  region = "us-east-1"  # Change to your desired region
}

# Create a security group allowing all traffic
resource "aws_security_group" "concert_buddy_1" {
  name        = "concert-buddy_0"
  description = "Allow all traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Find the latest Ubuntu AMI in the given region
data "aws_ami" "ubuntu" {
  most_recent = true

  owners = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}

# Define the user data script
resource "aws_instance" "fastapi_instance" {
  ami             = data.aws_ami.ubuntu.id
  instance_type   = "t2.micro"  # Change to the instance type you need
  security_groups = [aws_security_group.concert_buddy_1.name]

  user_data = <<-EOF
    #!/bin/bash
    export DEBIAN_FRONTEND=noninteractive

    # Update and install necessary packages
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip git
  EOF
}

output "public_ip" {
  value = aws_instance.fastapi_instance.public_ip
}

output "public_hostname" {
  value = aws_instance.fastapi_instance.public_dns
}

