from pprint import pprint
from datetime import datetime
from collections import defaultdict
"""
helper functions for json manipulation
"""
def simplify_response(data, hostname):
    data = data['return'][0]
    data = data[hostname]
    return data

"""
parsing functions for specific pages 
"""
def group_jobs_by_target(jobs_data):
    result = {}
    for job_id, job_details in jobs_data.items():
        targets = job_details.get('Target', [])
        if isinstance(targets, str):
            targets = [targets]
        for target in targets:
            result.setdefault(target, {})[job_id] = job_details
    return result


def sort_jobs_by_time(grouped_jobs):
    sorted_jobs = {}
    for target, jobs in grouped_jobs.items():
        sorted_jobs[target] = dict(
            sorted(
                jobs.items(),
                key=lambda x: datetime.strptime(x[1]['StartTime'], "%Y, %b %d %H:%M:%S.%f"),
                reverse=True
            )
        )
    return sorted_jobs


def clean_jobs(data):
    # list of functions to remove from the data
    excluded_functions = {
        "saltutil.find_job", 
        "runner.jobs.list_jobs", 
        "test.ping", 
        "runner.manage.up",
        "grains.item"
    }
    cleaned_data = {
        job_id: job_info
        for job_id, job_info in data.items()
        if not any(
            func.startswith("monitor") or func in excluded_functions 
            for func in job_info.get("Function", "").split(',')
        )
    }
    return cleaned_data


def clean_minion_data(data):
    keys = ['id', 'virtual', 'uuid', 'build_phase', 'role', 'fqdn_ip4']
    if not data:
        return False
    return {
        minion_id: {key: grain_data[key] for key in keys if key in grain_data}
        for minion_id, grain_data in data.items()
    }


def get_physical_minions(data, hostname):
  if data is None:
      return []
  
  minion_ids = []
  data = data.get('return', [{}])[0].get(hostname, {})
  
  for minion_id, grain_data in data.items():
      if grain_data.get('virtual') == 'physical':
          minion_ids.append(minion_id)
  
  return minion_ids


def sort_minions_by_role(data):
    sorted_data = defaultdict(list)
    for entry_id, entry in data.items():
        role = entry.get('role')
        if role is not None:
            sorted_data[role].append((entry_id, entry))
    return dict(sorted(sorted_data.items()))


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