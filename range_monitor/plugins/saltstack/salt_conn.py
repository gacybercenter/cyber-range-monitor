from . import salt_call
from . import parse
"""
called in the jobs route to collect all cached jobs
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
args = [cmd, tgt, [args]]
"""
def get_all_jobs():
  cmd = ('jobs.list_jobs', '')
  data_source = salt_call.salt_conn()
  jobs_json = salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", cmd)
  if 'API ERROR' in jobs_json:
    print("BAD DATA SOURCE FOUND IN get_all_jobs")
    return False
  grouped_jobs = parse.group_jobs_by_target(jobs_json)
  sorted_and_grouped_jobs = parse.sort_jobs_by_time(grouped_jobs)
  cleaned_data = parse.clean_jobs(sorted_and_grouped_jobs)
  return cleaned_data

"""
called in the default route to collect all minions
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
args = [cmd, tgt, [args]]
"""
def get_all_minions():
  data_source = salt_call.salt_conn()
  hostname = data_source['hostname']
  cmd = ['grains.items', '*']
  json_data = salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", cmd)
  if 'API ERROR' in json_data:
    print("BAD DATA SOURCE FOUND IN get_all_minions")
    return False
  minion_data = parse.clean_minion_data(json_data, hostname)
  minion_data = parse.sort_minions_by_role(minion_data)
  return minion_data

def get_specified_minion(minion_id):
  # x_cmd is an array used to pass commands to salt => [cmd, tgt, [args]]]
  uptime_cmd = ['status.uptime', minion_id]
  load_cmd = ['status.loadavg', minion_id]
  ipmi_cmd = ['grains.item', minion_id, ['ipmi']]
  # running commands passed into x_data using salt_call
  data_source = salt_call.salt_conn()
  hostname = data_source['hostname']
  uptime_data = {'uptime_data':salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", uptime_cmd)}
  load_data = {'load_data': salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'],  "monitor.salt_local_cmd", load_cmd)}
  ipmi_data = {'ipmi_data': salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", ipmi_cmd)}
  data_list = [uptime_data, load_data, ipmi_data]
  minion_data = parse.individual_minion_data(data_list, hostname)
  return minion_data

def get_ipmi_data(minion_id):
  ipmi_cmd = ['grains.item', minion_id, ['ipmi']]
  data_source = salt_call.salt_conn()
  ipmi_data = salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", ipmi_cmd)
  if 'API ERROR' in ipmi_data:
    print("BAD DATA SOURCE FOUND IN get_ipmi_data")
    return False
  return ipmi_data

def get_specified_job(job_id):
    # cmd is an array used to pass commands to salt => [cmd, tgt, [args]]
    cmd = ['jobs.lookup_jid', job_id]
    data_source = salt_call.salt_conn()
    job_data = salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", cmd)
    if 'API ERROR' in job_data:
      print("BAD DATA SOURCE FOUND IN get_specified_job")
      return False
    return job_data

def get_minion_count():
  cmd = ["manage.up"]
  data_source = salt_call.salt_conn()
  hostname = data_source['hostname']
  minions = salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], 'monitor.salt_run_cmd', cmd)
  data = parse.count_roles(minions, hostname)
  return data