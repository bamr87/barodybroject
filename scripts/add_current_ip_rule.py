import os
import requests
import boto3
import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '../src/.env'))

# Get AWS region and security group ID from environment (set SECURITY_GROUP_ID in .env)
AWS_REGION = env("DB_REGION", default="us-east-1")
SECURITY_GROUP_ID = env("SECURITY_GROUP_ID", default="")  # Must be provided

if not SECURITY_GROUP_ID:
    print("Error: SECURITY_GROUP_ID not set in your environment.")
    exit(1)

# Get current public IP
try:
    ip = requests.get("https://checkip.amazonaws.com").text.strip()
    cidr_ip = f"{ip}/32"
except Exception as e:
    print(f"Failed to retrieve public IP: {e}")
    exit(1)

# Initialize the EC2 client
ec2_client = boto3.client('ec2', region_name=AWS_REGION)

def add_ingress_rule():
    try:
        response = ec2_client.authorize_security_group_ingress(
            GroupId=SECURITY_GROUP_ID,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5432,
                    'ToPort': 5432,
                    'IpRanges': [{'CidrIp': cidr_ip, 'Description': 'Access for current machine'}],
                }
            ]
        )
        print(f"Successfully added ingress rule for {cidr_ip} on security group {SECURITY_GROUP_ID}.")
    except Exception as e:
        print(f"Failed to add ingress rule: {e}")

if __name__ == "__main__":
    add_ingress_rule()
