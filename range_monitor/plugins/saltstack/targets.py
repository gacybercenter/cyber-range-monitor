import json
# test json data
json_data = '''
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
shorter_json = '''
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


def sort_jobs_by_time(json_data):
    data = json_data
    sorted_jobs = {}
    for key, value in data.items():
        sorted_jobs[key] = dict(sorted(value.items(), key=lambda x: x[1]['StartTime'], reverse=True))
    return sorted_jobs

def clean_jobs(json_data):
    data = json_data
    excluded_functions = ["saltutil.find_job", "runner.jobs.list_jobs", "test.ping"]
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

# data = json.loads(json_data)

# # Group jobs by target
# grouped_data = group_jobs_by_target(data)

# # Sort jobs by StartTime within each target
# sorted_data = {}
# for target, jobs in grouped_data.items():
#     sorted_jobs = sorted(jobs.values(), key=lambda x: x['StartTime'], reverse=True)
#     sorted_data[target] = {job['StartTime']: job for job in sorted_jobs}

# # Print the sorted data
# print(json.dumps(sorted_data, indent=2))