import boto3
import json
import re
import sys

class ecs_service_scan:

  def __init__(self):

    self.services_list = []
    self.candidate_list = []
    self.candidate_dict = {}
    self.result_dict = {}

  def no_rollupdate(self, cluster_name, aws_profile='saml'):

    total_count = 0
    with_rollupdate_count = 0
    no_rollupdate_count = 0
    main_count = 0
    gery_count = 0

    ecs_session = boto3.Session(profile_name=aws_profile)

    ecs = ecs_session.client('ecs')

    # get first 100's service, maxResult maximum is 100
    services_response = ecs.list_services(cluster=cluster_name, maxResults=100)

    self.services_list.extend(services_response['serviceArns'])

    # get all of service 
    while 'nextToken' in services_response:

      services_response = ecs.list_services(cluster=cluster_name, maxResults=100, nextToken=services_response['nextToken'])

      self.services_list.extend(services_response['serviceArns'])

    # get all of serivces
    for i in range(len(self.services_list)):
      total_count = total_count + 1

      tmp_list = self.services_list[i].split("-")

      # get services are not gery service
      if not 'rollupdate' in tmp_list:
        self.candidate_list.append(self.services_list[i])
        main_count = main_count + 1
      else:
        gery_count = gery_count + 1  

    # add 'rollupdate' to main service for serach
    for i in range(len(self.candidate_list)):
      tmp_list = self.candidate_list[i].split("-")
      tmp_list.append('rollupdate')

      for j in range(len(self.services_list)):
        tmp1_list = self.services_list[j].split("-")
        
        # get main services which have gery service
        if len(set(tmp_list).difference(set(tmp1_list))) == 0:
          self.candidate_dict[self.candidate_list[i]] = "with_rollupdate_service"
          with_rollupdate_count = with_rollupdate_count + 1

   
    with_rollupdate_list = list(self.candidate_dict.keys())
    
    # remove main services which have gery service from main services have not gery service
    for i in range(len(with_rollupdate_list)):
      self.candidate_list.remove(with_rollupdate_list[i])
    

    for i in range(len(self.candidate_list)):
      self.result_dict[self.candidate_list[i]] = "no_rollupdate_service"
      no_rollupdate_count = no_rollupdate_count + 1

    self.result_dict['main_service']=str(main_count)
    self.result_dict['with_rollupdate_service']=str(with_rollupdate_count)
    self.result_dict['ecs_service_scan']=str(total_count)
    self.result_dict['no_rollupdate_service']=str(no_rollupdate_count)
    self.result_dict['gery_service']=str(gery_count)
    
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
  print (result.no_rollupdate(aws_profile=AWS_PROFILE, cluster_name=CLUSTER_NAME))

