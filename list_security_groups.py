import boto3
import csv
from botocore.exceptions import ClientError


def list_security_groups_and_open_ports():
    try:
        # Initialize a session using environment variables for credentials
        session = boto3.Session()

        # Initialize STS client to get the account ID
        sts = session.client('sts')
        account_id = sts.get_caller_identity().get('Account')
        
        # Initialize EC2 client
        ec2 = session.client('ec2')

        # Fetch all security groups
        security_groups = ec2.describe_security_groups()

        # Initialize a list to hold security group details
        security_group_details = []

        # Process each security group
        for sg in security_groups['SecurityGroups']:
            sg_info = {
                "Account ID": account_id,
                "Security Group ID": sg.get('GroupId'),
                "Security Group Name": sg.get('GroupName'),
                "Inbound Rules": [],
                "Outbound Rules": [],
                "Open to Internet Alert": False
            }

            # Check inbound rules
            for rule in sg.get('IpPermissions', []):
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        sg_info["Open to Internet Alert"] = True
                    sg_info["Inbound Rules"].append({
                        "Protocol": rule.get('IpProtocol'),
                        "Port Range": rule.get('FromPort', 'N/A') if rule.get('IpProtocol') != '-1' else "All",
                        "Source": ip_range.get('CidrIp')
                    })

            # Check outbound rules
            for rule in sg.get('IpPermissionsEgress', []):
                for ip_range in rule.get('IpRanges', []):
                    sg_info["Outbound Rules"].append({
                        "Protocol": rule.get('IpProtocol'),
                        "Port Range": rule.get('FromPort', 'N/A') if rule.get('IpProtocol') != '-1' else "All",
                        "Destination": ip_range.get('CidrIp')
                    })

            security_group_details.append(sg_info)

        # Write to CSV
        if security_group_details:
            with open('security_group_details.csv', mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["Account ID", "Security Group ID", "Security Group Name", "Inbound Rules", "Outbound Rules", "Open to Internet Alert"])
                writer.writeheader()
                for detail in security_group_details:
                    writer.writerow(detail)


        return security_group_details

    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
sg_details = list_security_groups_and_open_ports()
if sg_details:
    print("Security Group Details:")
#    for detail in sg_details:
#        print(detail)
else:
    print("No security groups found.")
