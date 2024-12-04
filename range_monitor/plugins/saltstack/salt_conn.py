from . import salt_call
from . import parse
import random 
import re

"""
helper functions to use saltstack api
"""
def execute_local_cmd(cmd):
  data_source = salt_call.salt_conn()
  return salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", cmd)

def execute_run_cmd(cmd):
  data_source = salt_call.salt_conn()
  return salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", cmd)

"""
cached information for session
"""
salt_cache = {
  'hostname': None,
  'physical_nodes': None
}

## MINIONS ##
"""
called in the default route to collect all minions
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
format for salt cmd = [cmd, tgt, [args]]
"""
def get_all_minions():
  cmd = ['grains.items', '*']
  json_data = execute_local_cmd(cmd)
  if salt_cache['hostname'] == None:
    data_source = salt_call.salt_conn()
    salt_cache['hostname'] = data_source['hostname']

  if 'API ERROR' in json_data:
    print("BAD DATA SOURCE FOUND IN get_all_minions")
    return False
  
  minion_data = parse.clean_minion_data(json_data, salt_cache['hostname'])
  minion_data = parse.sort_minions_by_role(minion_data)

  return minion_data

"""
called in the /minions/<string:minion_id> route to get advanced minion data
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
format for salt cmd = [cmd, tgt, [args]]
"""
def get_specified_minion(minion_id):
  uptime_cmd = ['status.uptime', minion_id]
  load_cmd = ['status.loadavg', minion_id]
  ipmi_cmd = ['grains.item', minion_id, ['ipmi']]

  uptime_data = {'uptime_data': execute_local_cmd(uptime_cmd)}
  load_data = {'load_data': execute_local_cmd(load_cmd)}
  ipmi_data = {'ipmi_data': execute_local_cmd(ipmi_cmd)}

  data_list = [uptime_data, load_data, ipmi_data]

  if salt_cache['hostname'] == None:
    data_source = salt_call.salt_conn()
    salt_cache['hostname'] = data_source['hostname']

  if 'API ERROR' in data_list:
    print("BAD DATA SOURCE FOUND IN get_all_minions")
    return False
  
  minion_data = parse.individual_minion_data(data_list, salt_cache['hostname'])
  return minion_data


## JOBS ##
"""
called in the jobs route to collect all cached jobs
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
format for salt cmd = [cmd, tgt, [args]]
"""
def get_all_jobs():
  cmd = ('jobs.list_jobs', '')
  jobs_json = execute_run_cmd(cmd)

  if 'API ERROR' in jobs_json:
    print("BAD DATA SOURCE FOUND IN get_all_jobs")
    return False
  
  grouped_jobs = parse.group_jobs_by_target(jobs_json)
  sorted_and_grouped_jobs = parse.sort_jobs_by_time(grouped_jobs)
  cleaned_data = parse.clean_jobs(sorted_and_grouped_jobs)

  return cleaned_data

"""
called in the /jobs/<string:job_id> route to get advanced job data
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
format for salt cmd = [cmd, tgt, [args]]
"""
def get_specified_job(job_id):
  # cmd is an array used to pass commands to salt => [cmd, tgt, [args]]
  cmd = ['jobs.lookup_jid', job_id]
  job_data = execute_run_cmd(cmd)

  if 'API ERROR' in job_data:
    print("BAD DATA SOURCE FOUND IN get_specified_job")
    return False
  
  return job_data


## PHYSICAL NODES ##
"""
called in the /minions/<string:minion_id> route to get advanced minion data
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
format for salt cmd = [cmd, tgt, [args]]
"""
def get_physical_nodes():
  if salt_cache['hostname'] == None:
    data_source = salt_call.salt_conn()
    salt_cache['hostname'] = data_source['hostname']

  if salt_cache['physical_nodes'] == None:
    cmd = ['grains.items', '*', ['virtual']]
    json_data = execute_local_cmd(cmd)
    salt_cache['physical_nodes'] = parse.get_physical_minions(json_data, salt_cache['hostname'])

    if 'API ERROR' in json_data:
      print("BAD DATA SOURCE FOUND IN get_all_minions")
      return False
  
  return salt_cache['physical_nodes']

def get_cpu_temp(minion_id):
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    pattern = r"\d{2}\.\d"
    cmd = ['grains.item', minion_id, ['ipmi']]
    ipmi_data = execute_local_cmd(cmd)
    hostname = salt_cache['hostname']

    if 'API ERROR' in ipmi_data:
      print("BAD DATA SOURCE FOUND IN get_cpu_temp")
      return False

    if 'return' in ipmi_data and isinstance(ipmi_data['return'], list) and len(ipmi_data['return']) > 0:
      salt_dev_data = ipmi_data['return'][0]
      if hostname in salt_dev_data and minion_id in salt_dev_data[hostname]:
        ipmi_info = salt_dev_data[hostname][minion_id]['ipmi']
        cpu_temp = ipmi_info['cpu_temp']
        match = re.search(pattern, cpu_temp)
        if match:
          return match.group()
        else:
          print("No match found")
    return None


def get_system_temp(minion_id):
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    pattern = r"\d{2}\.\d"
    cmd = ['grains.item', minion_id, ['ipmi']]
    ipmi_data = execute_local_cmd(cmd)
    hostname = salt_cache['hostname']

    if 'API ERROR' in ipmi_data:
      print("BAD DATA SOURCE FOUND IN get_system_temp")
      return False

    if 'return' in ipmi_data and isinstance(ipmi_data['return'], list) and len(ipmi_data['return']) > 0:
      salt_dev_data = ipmi_data['return'][0]
      if hostname in salt_dev_data and minion_id in salt_dev_data[hostname]:
        ipmi_info = salt_dev_data[hostname][minion_id]['ipmi']
        system_temp = ipmi_info['system_temp']
        match = re.search(pattern, system_temp)
        if match:
          return match.group()
        else:
          print("No match found")
    return None

## GRAPH INFORMATION ##
"""
called in the /graph routeto gather information to generate graph in javascript
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
format for salt cmd = [cmd, tgt, [args]]
"""
def get_minion_count():
  cmd = ["manage.up"]
  minions = execute_run_cmd(cmd)

  if salt_cache['hostname'] == None:
    data_source = salt_call.salt_conn()
    salt_cache['hostname'] = data_source['hostname']

  data = parse.count_roles(minions, salt_cache['hostname'])
  
  return data