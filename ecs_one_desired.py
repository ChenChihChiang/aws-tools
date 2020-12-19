import boto3
import json
import re
import sys

class ecs_service_scan:

  def __init__(self):

    self.services_list = []
    self.tasks_list = []
    self.result_dict = {}

  def one_desired(self, cluster_name, aws_profile='saml'):

    service_count = 0
    total_count = 0

    ecs_session = boto3.Session(profile_name=aws_profile)

    ecs = ecs_session.client('ecs')

    # get first 100's service, maxResult maximum is 100
    services_response = ecs.list_services(cluster=cluster_name, maxResults=100)

    self.services_list.extend(services_response['serviceArns'])

    # get all of service 
    while 'nextToken' in services_response:

      services_response = ecs.list_services(cluster=cluster_name, maxResults=100, nextToken=services_response['nextToken'])

      self.services_list.extend(services_response['serviceArns'])

    # get each task settings of each serivce
    for i in range(len(self.services_list)):
      total_count = total_count + 1
      svc_response = ecs.describe_services(
        cluster=cluster_name,
        services=[str(self.services_list[i])],
      )

      desiredCount = svc_response['services'][0]['deployments'][0]['desiredCount']

      if desiredCount == 1 and not re.search('rollupdate', self.services_list[i]):
        self.tasks_list.append(desiredCount)
        self.result_dict[self.services_list[i]] = list(self.tasks_list)
        self.tasks_list.clear()
        service_count = service_count + 1
    
    # count how many service be scanned
    self.result_dict['only_one_desired_service']=str(service_count)
    self.result_dict['ecs_service_scan']=str(total_count)
    return json.dumps(self.result_dict,sort_keys=True, indent=1)


if __name__ == '__main__':

  result = ecs_service_scan()

  if len(sys.argv) >= 3:
    AWS_PROFILE = sys.argv[1]
    CLUSTER_NAME = sys.argv[2]

  elif len(sys.argv) >= 2:
    AWS_PROFILE = sys.argv[1]

  else:
    AWS_PROFILE = 'default'
    CLUSTER_NAME = 'ecs-cluster'

  # scan only one desiredCount
  print (result.one_desired(aws_profile=AWS_PROFILE, cluster_name=CLUSTER_NAME))

