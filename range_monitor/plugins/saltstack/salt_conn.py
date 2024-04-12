from . import salt_call

"""
this is called in the jobs route to collect all cached jobs
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
"""
def get_all_jobs():
  job_info = ('jobs.list_jobs', '')
  data_source = salt_call.salt_conn()
  jobs_json = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.salt_run_cmd", job_info)
  parsed_json = {}
  for minion_id, data in jobs_json['return'][0]['salt-dev'].items():
    parsed_json[minion_id] = data
  print(parsed_json)
  return parsed_json

"""
this is called in the default route to collect all minions
returns: json returned by salt API cmd without "{'return': [{'salt-dev':" in front
"""
def get_all_minions():
  data_source = salt_call.salt_conn()
  args = ['id', 'osfinger', 'uuid', 'build_phase', 'role', 'fqdn_ip4', 'username']

  json_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.gather_minions_args", args)
  minion_data = json_data['return'][0]['salt-dev']
  print(minion_data)
  return minion_data


"""
this is called in the minion/[minion_id] route to show advanced minion informtion
returns: json with different information combined into one json file, ex: 
"""
def get_specified_minion(minion_id):
  # x_info is an array used to pass commands to salt => [tgt, cmd]
    uptime_info = [minion_id, 'status.uptime']
    load_info = [minion_id, 'status.loadavg']

    # running commands passed into x_array using salt_call
    data_source = salt_call.salt_conn()
    uptime_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.targeted_command", uptime_info)
    load_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'],  "monitor.targeted_command", load_info)

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
    # x_info is an array used to pass commands to salt => [tgt, cmd]
    job_info = ['*', 'saltutil.find_job', job_id]
    print(job_info)

    # running commands passed into x_array using salt_call
    data_source = salt_call.salt_conn()
    job_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.targeted_command", job_info)

    # creating minion_data nested dictionary with all necesary data
    print(f"Jobs data = {job_data}")