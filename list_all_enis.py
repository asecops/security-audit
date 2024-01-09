import boto3
import csv
from botocore.exceptions import ClientError


def list_all_enis():
    try:
        # Initialize a session using environment variables for credentials
        session = boto3.Session()

        # Initialize STS client to get the account ID
        sts = session.client('sts')
        account_id = sts.get_caller_identity().get('Account')
        
        # Initialize EC2 client
        ec2 = session.client('ec2')

        # Fetch all ENIs
        network_interfaces = ec2.describe_network_interfaces()

        # Initialize a list to hold ENI details
        enis_details = []

        # Extract relevant information for each ENI
        for eni in network_interfaces['NetworkInterfaces']:
            eni_info = {
                "Account ID": account_id,
                "ENI ID": eni.get('NetworkInterfaceId'),
                "Status": eni.get('Status'),
                "Private IP Address": eni.get('PrivateIpAddress'),
                "Public IP Address": eni.get('Association', {}).get('PublicIp'),
                "Attached Instance": eni.get('Attachment', {}).get('InstanceId'),
                "Security Groups": [sg['GroupName'] for sg in eni.get('Groups', [])]
            }
            enis_details.append(eni_info)

        # Write to CSV
        if enis_details:
          with open('eni_details.csv', mode='a', newline='') as file:
              writer = csv.DictWriter(file, fieldnames=["Account ID", "ENI ID", "Status", "Private IP Address", "Public IP Address", "Attached Instance", "Security Groups"])
              writer.writeheader()
              for detail in enis_details:
                  writer.writerow(detail)

        return enis_details

    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
enis_details = list_all_enis()
if enis_details:
    print("ENI Details:")
    #for detail in enis_details:
        #print(detail)
else:
    print("No ENIs found.")