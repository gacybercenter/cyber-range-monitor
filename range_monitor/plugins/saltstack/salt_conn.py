from . import salt_call
from . import parse
"""
this is called in the jobs route to collect all cached jobs
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
args = [cmd, tgt, [args]]
"""
def get_all_jobs():
  job_info = ('jobs.list_jobs', '')
  data_source = salt_call.salt_conn()
  jobs_json = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", job_info)
  if 'API ERROR' in jobs_json:
    print("BAD DATA SOURCE FOUND IN get_all_jobs")
    return False
  grouped_jobs = parse.group_jobs_by_target(jobs_json)
  sorted_and_grouped_jobs = parse.sort_jobs_by_time(grouped_jobs)
  cleaned_data = parse.clean_jobs(sorted_and_grouped_jobs)
  return cleaned_data

"""
this is called in the default route to collect all minions
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
args = [cmd, tgt, [args]]
"""
def get_all_minions():
  data_source = salt_call.salt_conn()
  minion_info = ['grains.items', '*']
  json_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", minion_info)
  if 'API ERROR' in json_data:
    print("BAD DATA SOURCE FOUND IN get_all_minions")
    return False
  minion_data = parse.clean_minion_data(json_data)
  minion_data = parse.sort_minions_by_role(minion_data)
  return minion_data


"""
this is called in the minion/[minion_id] route to show advanced minion informtion
returns: json with different information combined into one json file, ex: 
"""
def get_specified_minion(minion_id):
  # x_info is an array used to pass commands to salt => [cmd, tgt, [args]]]
    uptime_info = ['status.uptime', minion_id]
    load_info = ['status.loadavg', minion_id]

    # running commands passed into x_array using salt_call
    data_source = salt_call.salt_conn()
    uptime_data = {'uptime_data':salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", uptime_info)}
    load_data = {'load_data': salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'],  "monitor.salt_local_cmd", load_info)}
    data_list = [uptime_data, load_data]
    minion_data = parse.individual_minion_data(data_list)
    return minion_data

def get_specified_job(job_id):
    # x_info is an array used to pass commands to salt => [cmd, tgt, [args]]
    job_info = ['jobs.lookup_jid', job_id]
    data_source = salt_call.salt_conn()
    job_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", job_info)

def get_minion_count():
  call = ["manage.up"]
  data_source = salt_call.salt_conn()
  minions = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], 'monitor.salt_run_cmd', call)
  return minions