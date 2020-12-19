import boto3
import json
import sys


class ecs_service_scan:

  def __init__(self):

    self.services_list = []
    self.tasks_list = []
    self.result_dict = {}

  def status(self, cluster_name, aws_profile='saml'):

    count = 0

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
      count = count + 1
      svc_response = ecs.describe_services(
        cluster=cluster_name,
        services=[str(self.services_list[i])],
      )

      desiredCount = svc_response['services'][0]['deployments'][0]['desiredCount']
      runningCount = svc_response['services'][0]['deployments'][0]['runningCount']
      pendingCount = svc_response['services'][0]['deployments'][0]['pendingCount']


      if desiredCount != runningCount:
        self.tasks_list.append(desiredCount)
        self.tasks_list.append(runningCount)
        self.tasks_list.append(pendingCount)
        self.result_dict[self.services_list[i]] = list(self.tasks_list)
        self.tasks_list.clear()
    
    # count how many service be scanned 
    self.result_dict['ecs_service_scan']=str(count)
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

  # scan desiredCount != runningCount
  print (result.status(aws_profile=AWS_PROFILE, cluster_name=CLUSTER_NAME))

