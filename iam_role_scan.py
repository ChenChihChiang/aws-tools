import boto3
import json
import re
import sys

class iam_role_scan:

  def __init__(self):

    self.policy_list = []
    self.result_dict = {}
    self.tag_dict = {'Key': 'userrole', 'Value': 'y'}

  def search(self, filter_key, aws_profile='smal'):

    role_scan = 0

    iam_session = boto3.Session(profile_name=aws_profile)
    iam = iam_session.client('iam')

    # list all of roles 
    role_response = iam.list_roles(MaxItems=1000)

    for i in range(len(role_response['Roles'])):

      role_scan = role_scan + 1
      role_arn = role_response['Roles'][i]['Arn']
      role_name = role_response['Roles'][i]['RoleName']

      tag_response = iam.list_role_tags(RoleName=role_name)

      # filter out roles that are not apply for user
      if self.tag_dict not in tag_response['Tags']:

        policy_response = iam.list_attached_role_policies(
          RoleName=role_name
        )

        self.policy_list.clear() 

        # list the policies of roles
        for i in range(len(policy_response['AttachedPolicies'])):
          policy_name = policy_response['AttachedPolicies'][i]['PolicyName']
        
          # filter out the name of policies are not start with 'Customer'
          if re.search(filter_key, policy_name):
            self.policy_list.append(policy_name)
            
            if len(list(self.policy_list)) > 0:
              self.result_dict[role_arn] = list(self.policy_list)

    self.result_dict['role_scan'] = role_scan

    return json.dumps(self.result_dict,sort_keys=True, indent=1)


if __name__ == '__main__':

  result = iam_role_scan()

  if len(sys.argv) >= 2:
    AWS_PROFILE = sys.argv[1]
  else:
    AWS_PROFILE = 'default'

  print (result.search('^Customer',AWS_PROFILE))

