import json
from . import salt_call
from . import targets
"""
this is called in the jobs route to collect all cached jobs
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
args = [cmd, tgt, [args]]
"""
def get_all_jobs():
  job_info = ('jobs.list_jobs', '')
  data_source = salt_call.salt_conn()
  jobs_json = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", job_info)
  grouped_jobs = targets.group_jobs_by_target(jobs_json)
  sorted_and_grouped_jobs = targets.sort_jobs_by_time(grouped_jobs)
  cleaned_data = targets.clean_jobs(sorted_and_grouped_jobs)
  return cleaned_data

"""
this is called in the default route to collect all minions
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
args = [cmd, tgt, [args]]
"""
def get_all_minions():
  # data retrevial from salt
  data_source = salt_call.salt_conn()
  minion_info = ['grains.items', '*']
  json_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", minion_info)
  # parsing json data
  keys = ['id', 'osfinger', 'uuid', 'build_phase', 'role', 'fqdn_ip4', 'username']
  minions = {}
  json_data = json_data['return'][0]['salt-dev']
  for minion_id, grain_data in json_data.items():
      minions[minion_id] = {}
      for key in keys:
          minions[minion_id][key] = grain_data[key]
  print(minions)
  return minions


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
    uptime_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_local_cmd", uptime_info)
    load_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'],  "monitor.salt_local_cmd", load_info)
    # creating minion_data nested dictionary with all necesary data
    minion_data = {}
    for data_item in uptime_data['return']:
        for master_id, master_data in data_item.items():
            if minion_id in master_data:
                uptime = master_data[minion_id]
                for load_item in load_data['return']:
                    if minion_id in load_item.get(master_id, {}):
                        load = load_item[master_id][minion_id]
                        minion_data[minion_id] = {'uptime_data': uptime, 'load_data': load}
    print(f"Minion data: {minion_data}")
    return minion_data

def get_specified_job(job_id):
    # x_info is an array used to pass commands to salt => [cmd, tgt, [args]]
    job_info = ['jobs.lookup_jid', job_id]
    print(job_info)

    # running commands passed into x_array using salt_call
    data_source = salt_call.salt_conn()
    job_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", job_info)

    # creating minion_data nested dictionary with all necesary data
    print(f"Jobs data = {job_data}")