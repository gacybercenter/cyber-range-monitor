from jsonpath_rw import jsonpath, parse
"""
groups jobs by target - each target has a dictionary of jobs
"""
def group_jobs_by_target(json_data):
    data = json_data
    grouped_jobs = {}
    for item in data['return']:
        for _, jobs in item.items():
            for job_id, job_data in jobs.items():
                targets = job_data['Target']
                if isinstance(targets, str):
                    targets = [targets]
                for target in targets:
                    if target not in grouped_jobs:
                        grouped_jobs[target] = {}
                    grouped_jobs[target][job_id] = job_data
    return grouped_jobs

def group_jobs_with_library(json_data):
    grouped_jobs = {}
    jsonpath_expr = parse('$.return[*].*')

    for match in jsonpath_expr.find(json_data):
        jobs = match.value
        for job_id, job_data in jobs.items():
            targets = job_data['Target']
            if isinstance(targets, str):
                targets = [targets]
            for target in targets:
                if target not in grouped_jobs:
                    grouped_jobs[target] = {}
                grouped_jobs[target][job_id] = job_data

    return grouped_jobs

def sort_jobs_by_time(json_data):
    data = json_data
    sorted_jobs = {}
    for key, value in data.items():
        sorted_jobs[key] = dict(sorted(value.items(), key=lambda x: x[1]['StartTime'], reverse=True))
    return sorted_jobs

def clean_jobs(json_data):
    data = json_data
    excluded_functions = ["saltutil.find_job", "runner.jobs.list_jobs", "test.ping", "runner.manage.up"]
    cleaned_data = {}
    for key, value in data.items():
        exclude_job = False
        for job_id, job_info in value.items():
            function = job_info.get("Function", None)
            if any(function.startswith("monitor") or function in excluded_functions for function in function.split(',')):
                exclude_job = True
                break
        if not exclude_job:
            cleaned_data[key] = value
    return cleaned_data

def clean_minion_data(data, hostname):
    keys = ['id', 'virtual', 'uuid', 'build_phase', 'role', 'fqdn_ip4', 'username']
    minions={}
    if data is None:
        return False
    data = data['return'][0][hostname]
    for minion_id, grain_data in data.items():
        minions[minion_id] = {}
        for key in keys:
            minions[minion_id][key] = grain_data[key]
    return minions


def individual_minion_data(input_data, hostname):
    minion_data = {}
    for entry in input_data:
        if isinstance(entry, dict):
            for key, value in entry.items():
                for minion_id, minion_info in value['return'][0].items():
                    if minion_id not in minion_data:
                        minion_data[minion_id] = {}
                    if key not in minion_data[minion_id]:
                        minion_data[minion_id][key] = {}
                    minion_data[minion_id][key].update(minion_info)
    return minion_data[hostname]

def sort_minions_by_role(data):
    sorted_data = {}
    roles = set(entry['role'] for entry in data.values())
    for role in roles:
        sorted_data[role] = []
    for entry_id, entry in data.items():
        role = entry['role']
        sorted_data[role].append((entry_id, entry))
    myKeys = list(sorted_data.keys())
    myKeys.sort()
    sorted_dict = {i: sorted_data[i] for i in myKeys}
    return sorted_dict

def count_roles(data, hostname):
    role_counts = {}
    items= data['return'][0][hostname]

    for item in items:
        role = item.split('-')[0]
        if role in role_counts:
            role_counts[role] += 1
        else:
            role_counts[role] = 1
    
    x = list(role_counts.keys())
    y = list(role_counts.values())
    return {'x': x, 'y': y}


# test json data
test_json_data = '''
{
  "return": [
    {
      "salt-dev": {
        "20240410161705250425": {
          "Function": "monitor.gather_minions_args",
          "Arguments": [
            ["id", "osfinger", "uuid", "build_phase", "role", "fqdn_ip4", "username"]
          ],
          "Target": "salt-dev",
          "Target-type": "glob",
          "User": "api",
          "StartTime": "2024, Apr 10 16:17:05.250425"
        },
        "20240410153708326437": {
          "Function": "monitor.gather_minions_args",
          "Arguments": [
            ["id", "osfinger", "uuid", "build_phase", "role", "fqdn_ip4", "username"]
          ],
          "Target": "salt-dev",
          "Target-type": "glob",
          "User": "api",
          "StartTime": "2024, Apr 10 15:37:08.326437"
        },
        "20240410131531700729": {
          "Function": "saltutil.find_job",
          "Arguments": ["20240410131516336616"],
          "Target": [
            "controllerv2-db943b2c-66f8-5a95-9c10-bc3e2e012a05",
            "controller-f0cde7fa-c220-5152-970b-725bbb008509",
            "cache-079ca7ac-4184-52fb-b970-01392ddf8753",
            "haproxy-930780e3-4565-58eb-9e4f-1ce21538b3d2",
            "salt-dev",
            "pxe-dev"
          ],
          "Target-type": "list",
          "User": "root",
          "StartTime": "2024, Apr 10 13:15:31.700729"
        }
      }
    }
  ]
}
'''
shorter_test_json = '''
  {
  "salt-dev": {
    "20240410161705250425": {
      "Function": "monitor.gather_minions_args",
      "Arguments": [
        "id",
        "osfinger",
        "uuid",
        "build_phase",
        "role",
        "fqdn_ip4",
        "username"
      ],
      "Target": "salt-dev",
      "Target-type": "glob",
      "User": "api",
      "StartTime": "2024, Apr 10 16:17:05.250425"
    },
    "20240410153708326437": {
      "Function": "monitor.gather_minions_args",
      "Arguments": [
        "id",
        "osfinger",
        "uuid",
        "build_phase",
        "role",
        "fqdn_ip4",
        "username"
      ],
      "Target": "salt-dev",
      "Target-type": "glob",
      "User": "api",
      "StartTime": "2024, Apr 10 15:37:08.326437"
    },
    "20240410131531700729": {
      "Function": "saltutil.find_job",
      "Arguments": ["20240410131516336616"],
      "Target": [
        "controllerv2-db943b2c-66f8-5a95-9c10-bc3e2e012a05",
        "controller-f0cde7fa-c220-5152-970b-725bbb008509",
        "cache-079ca7ac-4184-52fb-b970-01392ddf8753",
        "haproxy-930780e3-4565-58eb-9e4f-1ce21538b3d2",
        "salt-dev",
        "pxe-dev"
      ],
      "Target-type": "list",
      "User": "root",
      "StartTime": "2024, Apr 10 13:15:31.700729"
    }
  }
}
'''

print(group_jobs_with_library(shorter_test_json))