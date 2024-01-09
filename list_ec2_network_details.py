import boto3
import csv
from botocore.exceptions import ClientError

def list_ec2_network_details():
    try:
        # Initialize a session using environment variables for credentials
        session = boto3.Session()

        # Initialize STS client to get the account ID
        sts = session.client('sts')
        account_id = sts.get_caller_identity().get('Account')
        
        # Initialize EC2 client
        ec2 = session.client('ec2')

        # Fetch all EC2 instances
        ec2_instances = ec2.describe_instances()

        # Initialize a list to hold instance network details
        instances_network_details = []

        # Extract network-related information for each instance
        for reservation in ec2_instances['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    "Account ID": account_id,
                    "Instance ID": instance.get('InstanceId'),
                    "Public IP Address": instance.get('PublicIpAddress'),
                    "Private IP Address": instance.get('PrivateIpAddress'),
                    "Security Groups": instance.get('SecurityGroups'),
                    "ENI Count": len(instance.get('NetworkInterfaces', []))
                }
                instances_network_details.append(instance_info)

        # Write to CSV
        if instances_network_details:
            with open('ec2_network_details.csv', mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Account ID","Instance ID", "Public IP Address", "Private IP Address", "Security Groups", "ENI Count"])
                writer.writeheader()
                for detail in instances_network_details:
                    writer.writerow(detail)

        return instances_network_details

    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
network_details = list_ec2_network_details()
if network_details:
    print("EC2 Instance Network Details:")
    #for detail in network_details:
        #print(detail)
else:
    print("No EC2 instances found.")
