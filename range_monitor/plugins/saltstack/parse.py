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

def clean_minion_data(data):
    keys = ['id', 'osfinger', 'uuid', 'build_phase', 'role', 'fqdn_ip4', 'username']
    minions={}
    if data is None:
        return False
    print(F"uncleaned data", data)
    data = data['return'][0]['salt-dev']
    for minion_id, grain_data in data.items():
        minions[minion_id] = {}
        for key in keys:
            minions[minion_id][key] = grain_data[key]
    return minions


def individual_minion_data(input_data):
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
    return minion_data['salt-dev']

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

test_minions = {'arm-3733c7e6-8b04-541b-90b6-a09eb866e529': {'id': 'arm-3733c7e6-8b04-541b-90b6-a09eb866e529', 'osfinger': 'Ubuntu-22.04', 'uuid': '8f71d200-d06c-11ed-8000-7cc2558257d8', 'build_phase': 'configure', 'role': 'compute', 'fqdn_ip4': ['10.200.1.68'], 'username': 'root'}, 'arm-0045789e-49a2-5c78-86fe-7c61e6caa2e7': {'id': 'arm-0045789e-49a2-5c78-86fe-7c61e6caa2e7', 'osfinger': 'Ubuntu-22.04', 'uuid': '54849400-d096-11ed-8000-7cc255825848', 'build_phase': 'configure', 'role': 'compute', 'fqdn_ip4': ['10.200.1.69'], 'username': 'root'}, 'storage-16f3d486-648e-5805-a153-f25f552aac7f': {'id': 'storage-16f3d486-648e-5805-a153-f25f552aac7f', 'osfinger': 'Ubuntu-22.04', 'uuid': '00000000-0000-0000-0000-ac1f6bb6df2f', 'build_phase': 'configure', 'role': 'storage', 'fqdn_ip4': ['10.200.1.170'], 'username': 'root'}, 'storage-d06d1ed7-3a90-5283-81d2-b78712175b66': {'id': 'storage-d06d1ed7-3a90-5283-81d2-b78712175b66', 'osfinger': 'Ubuntu-22.04', 'uuid': '00000000-0000-0000-0000-ac1f6bb6df12', 'build_phase': 'configure', 'role': 'storage', 'fqdn_ip4': ['10.200.1.171'], 'username': 'root'}, 'storage-f0ad44c9-0e23-59c3-98fb-2b7086a6df68': {'id': 'storage-f0ad44c9-0e23-59c3-98fb-2b7086a6df68', 'osfinger': 'Ubuntu-22.04', 'uuid': '00000000-0000-0000-0000-ac1f6bb6df22', 'build_phase': 'configure', 'role': 'storage', 'fqdn_ip4': ['10.200.1.172'], 'username': 'root'}, 'compute-7c0d81ac-576d-5965-a6a0-921f1dc2c777': {'id': 'compute-7c0d81ac-576d-5965-a6a0-921f1dc2c777', 'osfinger': 'Ubuntu-22.04', 'uuid': '00000000-0000-0000-0000-0cc47afbf3b4', 'build_phase': 'configure', 'role': 'compute', 'fqdn_ip4': ['10.200.1.53'], 'username': 'root'}, 'compute-b0c6e5e3-1c1e-5b1c-8854-ce95892f4e5a': {'id': 'compute-b0c6e5e3-1c1e-5b1c-8854-ce95892f4e5a', 'osfinger': 'Ubuntu-22.04', 'uuid': '00000000-0000-0000-0000-0cc47afbf274', 'build_phase': 'configure', 'role': 'compute', 'fqdn_ip4': ['10.200.1.52'], 'username': 'root'}, 'compute-24266c79-9f54-5047-b814-41d4dfadfcca': {'id': 'compute-24266c79-9f54-5047-b814-41d4dfadfcca', 'osfinger': 'Ubuntu-22.04', 'uuid': '00000000-0000-0000-0000-0cc47afbf39c', 'build_phase': 'configure', 'role': 'compute', 'fqdn_ip4': ['10.200.1.54'], 'username': 'root'}, 'salt-dev': {'id': 'salt-dev', 'osfinger': 'Ubuntu-22.04', 'uuid': '2e939311-7d4f-4c4d-81a3-603f98fcc1d1', 'build_phase': 'configure', 'role': 'salt', 'fqdn_ip4': ['10.200.1.31'], 'username': 'root'}, 'guacamole-9b5ede54-3db8-563a-9c45-fbd74a7b844c': {'id': 'guacamole-9b5ede54-3db8-563a-9c45-fbd74a7b844c', 'osfinger': 'Ubuntu-22.04', 'uuid': '90573a29-d714-4189-b629-c05958555708', 'build_phase': 'configure', 'role': 'guacamole', 'fqdn_ip4': ['10.200.1.160'], 'username': 'root'}, 'rabbitmq-55a00562-ae15-58a9-af7f-3ad811580580': {'id': 'rabbitmq-55a00562-ae15-58a9-af7f-3ad811580580', 'osfinger': 'Ubuntu-22.04', 'uuid': '5aa79ae8-8280-4c01-855d-581624dcb23e', 'build_phase': 'configure', 'role': 'rabbitmq', 'fqdn_ip4': ['10.200.1.153'], 'username': 'root'}, 'rabbitmq-e5d71a31-1036-58ac-808c-cace384f8432': {'id': 'rabbitmq-e5d71a31-1036-58ac-808c-cace384f8432', 'osfinger': 'Ubuntu-22.04', 'uuid': '76d9321c-79a4-4019-94b7-d6542ddbd040', 'build_phase': 'configure', 'role': 'rabbitmq', 'fqdn_ip4': ['10.200.1.155'], 'username': 'root'}, 'horizon-73793712-a410-5314-aeb1-7853af144490': {'id': 'horizon-73793712-a410-5314-aeb1-7853af144490', 'osfinger': 'Ubuntu-22.04', 'uuid': 'a8ef6564-4692-4e49-b929-3bfc3b6a3e85', 'build_phase': 'configure', 'role': 'horizon', 'fqdn_ip4': ['10.200.1.165'], 'username': 'root'}, 'glance-b8d004ae-dde6-572f-a174-d823b208917d': {'id': 'glance-b8d004ae-dde6-572f-a174-d823b208917d', 'osfinger': 'Ubuntu-22.04', 'uuid': '891a140b-b513-485a-a467-b3e88656ef9d', 'build_phase': 'configure', 'role': 'glance', 'fqdn_ip4': ['10.200.1.188'], 'username': 'root'}, 'neutron-3546d004-af58-5dff-9727-b70531e52519': {'id': 'neutron-3546d004-af58-5dff-9727-b70531e52519', 'osfinger': 'Ubuntu-22.04', 'uuid': '7f17bd26-981e-4461-a497-fd21f6aa42df', 'build_phase': 'configure', 'role': 'neutron', 'fqdn_ip4': ['10.200.1.60'], 'username': 'root'}, 'network-10871b79-dde6-5a7f-8c73-0063e0c2687e': {'id': 'network-10871b79-dde6-5a7f-8c73-0063e0c2687e', 'osfinger': 'Ubuntu-22.04', 'uuid': 'a7ed051e-9b30-457f-8fdd-b3bbb19e0799', 'build_phase': 'configure', 'role': 'network', 'fqdn_ip4': ['10.200.1.187'], 'username': 'root'}, 'network-e88649ab-c485-568d-abbd-3c3cc96b62e2': {'id': 'network-e88649ab-c485-568d-abbd-3c3cc96b62e2', 'osfinger': 'Ubuntu-22.04', 'uuid': '63b6f689-e444-4250-b812-d99e52e18137', 'build_phase': 'configure', 'role': 'network', 'fqdn_ip4': ['10.200.1.184'], 'username': 'root'}, 'heat-c708f428-43bc-59e2-b294-694add097aa1': {'id': 'heat-c708f428-43bc-59e2-b294-694add097aa1', 'osfinger': 'Ubuntu-22.04', 'uuid': 'e86cafc8-ed98-47ea-ba25-f40c0ea327ba', 'build_phase': 'configure', 'role': 'heat', 'fqdn_ip4': ['10.200.1.173'], 'username': 'root'}, 'etcd-89bc4407-e6da-57cc-851c-442280a0c3c5': {'id': 'etcd-89bc4407-e6da-57cc-851c-442280a0c3c5', 'osfinger': 'Ubuntu-22.04', 'uuid': '30e1cd20-d692-4fd6-a728-26505c317458', 'build_phase': 'configure', 'role': 'etcd', 'fqdn_ip4': ['10.200.1.150'], 'username': 'root'}, 'guacamole-c87194e8-1b35-5624-a40f-d6b6683d21ae': {'id': 'guacamole-c87194e8-1b35-5624-a40f-d6b6683d21ae', 'osfinger': 'Ubuntu-22.04', 'uuid': 'b0b8b9cf-3fd9-4f25-af93-3f1de201f3e2', 'build_phase': 'configure', 'role': 'guacamole', 'fqdn_ip4': ['10.200.1.161'], 'username': 'root'}, 'cinder-17f044a6-8dc6-5bef-999b-00e8b9c13244': {'id': 'cinder-17f044a6-8dc6-5bef-999b-00e8b9c13244', 'osfinger': 'Ubuntu-22.04', 'uuid': 'd985d986-29f8-49bd-901a-3c1ae09920bc', 'build_phase': 'configure', 'role': 'cinder', 'fqdn_ip4': ['10.200.1.196'], 'username': 'root'}, 'horizon-39ce2f25-e852-5078-a8ea-bf9dfa9adffc': {'id': 'horizon-39ce2f25-e852-5078-a8ea-bf9dfa9adffc', 'osfinger': 'Ubuntu-22.04', 'uuid': '76c54360-0a79-45f9-b98a-1b760e52b3bd', 'build_phase': 'configure', 'role': 'horizon', 'fqdn_ip4': ['10.200.1.166'], 'username': 'root'}, 'bind-6ec4c16f-8d86-556c-b69d-c51d6dcb1039': {'id': 'bind-6ec4c16f-8d86-556c-b69d-c51d6dcb1039', 'osfinger': 'Ubuntu-22.04', 'uuid': '72e09f63-d5f6-4a06-8443-42da74d4f35c', 'build_phase': 'configure', 'role': 'bind', 'fqdn_ip4': ['10.200.1.65'], 'username': 'root'}, 'memcached-34c91392-e0d3-5b5a-85d2-d0bcba13c379': {'id': 'memcached-34c91392-e0d3-5b5a-85d2-d0bcba13c379', 'osfinger': 'Ubuntu-22.04', 'uuid': '2e83d9ed-5163-4086-aa3f-41e50a2c4418', 'build_phase': 'configure', 'role': 'memcached', 'fqdn_ip4': ['10.200.1.156'], 'username': 'root'}, 'pxe-dev': {'id': 'pxe-dev', 'osfinger': 'Ubuntu-22.04', 'uuid': '4857ff46-a377-4244-9718-8835abbc7984', 'build_phase': 'configure', 'role': 'pxe', 'fqdn_ip4': ['10.200.1.30'], 'username': 'root'}, 'bind-6ce83ecd-8e93-5878-9ea6-6cffea4fb9b6': {'id': 'bind-6ce83ecd-8e93-5878-9ea6-6cffea4fb9b6', 'osfinger': 'Ubuntu-22.04', 'uuid': 'ffa0cd83-a955-4d9c-a68d-50e8b3a35cc5', 'build_phase': 'configure', 'role': 'bind', 'fqdn_ip4': ['10.200.1.64'], 'username': 'root'}, 'nova-5afca932-b321-5adf-b0ca-a1a05b3991eb': {'id': 'nova-5afca932-b321-5adf-b0ca-a1a05b3991eb', 'osfinger': 'Ubuntu-22.04', 'uuid': '59e76250-8a06-4648-86af-db9b58f38e1b', 'build_phase': 'configure', 'role': 'nova', 'fqdn_ip4': ['10.200.1.189'], 'username': 'root'}, 'cephmon-a922a07f-af55-5c12-bee1-36d9bf47d4d6': {'id': 'cephmon-a922a07f-af55-5c12-bee1-36d9bf47d4d6', 'osfinger': 'Ubuntu-22.04', 'uuid': 'e9d3d47c-aaa8-4c40-9454-7c852c20115d', 'build_phase': 'configure', 'role': 'cephmon', 'fqdn_ip4': ['10.200.1.147'], 'username': 'root'}, 'volume-54ed9eea-8ad8-5339-a873-1a39af82b004': {'id': 'volume-54ed9eea-8ad8-5339-a873-1a39af82b004', 'osfinger': 'Ubuntu-22.04', 'uuid': '1f511448-bab1-4e19-91b4-091c678502f3', 'build_phase': 'configure', 'role': 'volume', 'fqdn_ip4': ['10.200.1.197'], 'username': 'root'}, 'bind-60924a51-2ad8-5440-99dd-5cf09bcf7b8b': {'id': 'bind-60924a51-2ad8-5440-99dd-5cf09bcf7b8b', 'osfinger': 'Ubuntu-22.04', 'uuid': '45f9b39b-bfef-460b-b892-9d39a6f2dba9', 'build_phase': 'configure', 'role': 'bind', 'fqdn_ip4': ['10.200.1.63'], 'username': 'root'}, 'designate-56e02c4f-33a7-5e89-8d4c-f2749f97d0cd': {'id': 'designate-56e02c4f-33a7-5e89-8d4c-f2749f97d0cd', 'osfinger': 'Ubuntu-22.04', 'uuid': 'e02a2ab9-994b-4123-ac7b-14e01498797f', 'build_phase': 'configure', 'role': 'designate', 'fqdn_ip4': ['10.200.1.179'], 'username': 'root'}, 'network-99d484b0-177b-5a01-b9fc-113b08b253f2': {'id': 'network-99d484b0-177b-5a01-b9fc-113b08b253f2', 'osfinger': 'Ubuntu-22.04', 'uuid': '97f1cbdc-6942-4643-9069-e6ee92bcf5f5', 'build_phase': 'configure', 'role': 'network', 'fqdn_ip4': ['10.200.1.182'], 'username': 'root'}, 'etcd-33ad2abe-76de-5476-bed1-961b099636d9': {'id': 'etcd-33ad2abe-76de-5476-bed1-961b099636d9', 'osfinger': 'Ubuntu-22.04', 'uuid': '6a01194b-86a3-4c7c-9218-5c0904a3d920', 'build_phase': 'configure', 'role': 'etcd', 'fqdn_ip4': ['10.200.1.148'], 'username': 'root'}, 'volume-4d5e6579-8733-5a58-9d53-aca39c400932': {'id': 'volume-4d5e6579-8733-5a58-9d53-aca39c400932', 'osfinger': 'Ubuntu-22.04', 'uuid': '213afe40-b2ee-4b00-b5e5-d2f7798f4556', 'build_phase': 'configure', 'role': 'volume', 'fqdn_ip4': ['10.200.1.199'], 'username': 'root'}, 'cephmon-89b9949f-6ed8-5b34-a625-395f484e3783': {'id': 'cephmon-89b9949f-6ed8-5b34-a625-395f484e3783', 'osfinger': 'Ubuntu-22.04', 'uuid': '6e03a020-ed14-4963-88da-7710704bf1d9', 'build_phase': 'configure', 'role': 'cephmon', 'fqdn_ip4': ['10.200.1.146'], 'username': 'root'}, 'placement-0cc0a5d1-d6c2-5865-b2e2-15618d9446f6': {'id': 'placement-0cc0a5d1-d6c2-5865-b2e2-15618d9446f6', 'osfinger': 'Ubuntu-22.04', 'uuid': '9dc7ce16-da4b-42da-a954-946965fd8e7f', 'build_phase': 'configure', 'role': 'placement', 'fqdn_ip4': ['10.200.1.186'], 'username': 'root'}, 'memcached-b9b2f234-8746-5844-9245-33b3f370c010': {'id': 'memcached-b9b2f234-8746-5844-9245-33b3f370c010', 'osfinger': 'Ubuntu-22.04', 'uuid': 'a0e379da-d01d-4025-b178-87f7bdc5ce08', 'build_phase': 'configure', 'role': 'memcached', 'fqdn_ip4': ['10.200.1.159'], 'username': 'root'}, 'keystone-725f292a-1e22-543e-82a7-15d3f918cc14': {'id': 'keystone-725f292a-1e22-543e-82a7-15d3f918cc14', 'osfinger': 'Ubuntu-22.04', 'uuid': '32125e26-b2f5-42f4-9287-13aea8fca771', 'build_phase': 'configure', 'role': 'keystone', 'fqdn_ip4': ['10.200.1.168'], 'username': 'root'}, 'swift-a3cf6c0f-0139-53a4-9e8f-8395b12e20b2': {'id': 'swift-a3cf6c0f-0139-53a4-9e8f-8395b12e20b2', 'osfinger': 'Ubuntu-22.04', 'uuid': '0d63452a-57fc-4358-bbd5-b0eb7254436c', 'build_phase': 'configure', 'role': 'swift', 'fqdn_ip4': ['10.200.1.192'], 'username': 'root'}, 'memcached-0814b9cf-303c-5696-8a69-2c296384f659': {'id': 'memcached-0814b9cf-303c-5696-8a69-2c296384f659', 'osfinger': 'Ubuntu-22.04', 'uuid': 'db589d14-91e6-4d2a-b2e8-09ca91cd4c8a', 'build_phase': 'configure', 'role': 'memcached', 'fqdn_ip4': ['10.200.1.158'], 'username': 'root'}, 'keystone-08c0ea20-cd6a-5411-93f7-e932e6a30471': {'id': 'keystone-08c0ea20-cd6a-5411-93f7-e932e6a30471', 'osfinger': 'Ubuntu-22.04', 'uuid': '0180d6d6-be77-4f2f-af29-a26e7caaa386', 'build_phase': 'configure', 'role': 'keystone', 'fqdn_ip4': ['10.200.1.169'], 'username': 'root'}, 'etcd-31fdc67e-f6d1-5c38-abd7-e2e60ad7696a': {'id': 'etcd-31fdc67e-f6d1-5c38-abd7-e2e60ad7696a', 'osfinger': 'Ubuntu-22.04', 'uuid': 'e388962d-91f4-4084-a3ee-ebf4c1ff43a8', 'build_phase': 'configure', 'role': 'etcd', 'fqdn_ip4': ['10.200.1.149'], 'username': 'root'}, 'nova-4aef9987-f41d-58fb-9047-ff6beaa3fc7f': {'id': 'nova-4aef9987-f41d-58fb-9047-ff6beaa3fc7f', 'osfinger': 'Ubuntu-22.04', 'uuid': '1668d7fd-547a-4141-a3a9-16fd80cc8faf', 'build_phase': 'configure', 'role': 'nova', 'fqdn_ip4': ['10.200.1.193'], 'username': 'root'}, 'keystone-6324c98f-ff57-56bd-9242-8adf7065d7bb': {'id': 'keystone-6324c98f-ff57-56bd-9242-8adf7065d7bb', 'osfinger': 'Ubuntu-22.04', 'uuid': '64a548f3-427d-42f9-9519-e27c77d3c669', 'build_phase': 'configure', 'role': 'keystone', 'fqdn_ip4': ['10.200.1.167'], 'username': 'root'}, 'swift-811d2c12-3e55-59fe-916b-1f2511c02c69': {'id': 'swift-811d2c12-3e55-59fe-916b-1f2511c02c69', 'osfinger': 'Ubuntu-22.04', 'uuid': '12dcdb30-9869-4751-8a4b-59b7112a3f6d', 'build_phase': 'configure', 'role': 'swift', 'fqdn_ip4': ['10.200.1.194'], 'username': 'root'}, 'controllerv2-b7b0cc47-c129-58a2-b5a9-ede64731c91f': {'id': 'controllerv2-b7b0cc47-c129-58a2-b5a9-ede64731c91f', 'osfinger': 'Ubuntu-22.04', 'uuid': 'b1058200-6286-11eb-8000-3cecef4bafcc', 'build_phase': 'configure', 'role': 'controller', 'fqdn_ip4': ['10.200.1.58'], 'username': 'root'}, 'mysql-5d0c3804-0738-5dee-b47a-7cb61a57620a': {'id': 'mysql-5d0c3804-0738-5dee-b47a-7cb61a57620a', 'osfinger': 'Ubuntu-22.04', 'uuid': 'bdf799cd-eb17-40b6-9eae-29a3b83d938e', 'build_phase': 'configure', 'role': 'mysql', 'fqdn_ip4': ['10.200.1.57'], 'username': 'root'}, 'mysql-1d10768e-1cee-5c83-9524-6c639c1d0f36': {'id': 'mysql-1d10768e-1cee-5c83-9524-6c639c1d0f36', 'osfinger': 'Ubuntu-22.04', 'uuid': '913e251f-76e4-4b15-9910-925c23d1a520', 'build_phase': 'configure', 'role': 'mysql', 'fqdn_ip4': ['10.200.1.59'], 'username': 'root'}, 'neutron-d66f7e1b-8e1c-5669-9032-f22f1f8d0904': {'id': 'neutron-d66f7e1b-8e1c-5669-9032-f22f1f8d0904', 'osfinger': 'Ubuntu-22.04', 'uuid': 'b8a4d911-c407-4e82-9eb0-f3a323084ba8', 'build_phase': 'configure', 'role': 'neutron', 'fqdn_ip4': ['10.200.1.61'], 'username': 'root'}, 'cephmon-3cf8c3eb-c18f-5f5a-bb12-41785d49406d': {'id': 'cephmon-3cf8c3eb-c18f-5f5a-bb12-41785d49406d', 'osfinger': 'Ubuntu-22.04', 'uuid': '21d23ba8-90bd-431e-ae37-d8cf4b16e09e', 'build_phase': 'configure', 'role': 'cephmon', 'fqdn_ip4': ['10.200.1.145'], 'username': 'root'}, 'cinder-63d8d547-0817-5022-b2e0-9d3aceb346a1': {'id': 'cinder-63d8d547-0817-5022-b2e0-9d3aceb346a1', 'osfinger': 'Ubuntu-22.04', 'uuid': '9b55375b-4104-4438-bff8-29cdbbe812b1', 'build_phase': 'configure', 'role': 'cinder', 'fqdn_ip4': ['10.200.1.195'], 'username': 'root'}, 'neutron-d61ff79d-1ad5-5b97-a2d9-964edd9eba7e': {'id': 'neutron-d61ff79d-1ad5-5b97-a2d9-964edd9eba7e', 'osfinger': 'Ubuntu-22.04', 'uuid': '0e204d4b-d77d-45fd-bc7a-c40c496d98b9', 'build_phase': 'configure', 'role': 'neutron', 'fqdn_ip4': ['10.200.1.62'], 'username': 'root'}, 'designate-55009e04-0f7a-5fb4-b131-d28a58dd8f4c': {'id': 'designate-55009e04-0f7a-5fb4-b131-d28a58dd8f4c', 'osfinger': 'Ubuntu-22.04', 'uuid': '7e869cfa-742f-4e2b-afc2-a64bdae4550a', 'build_phase': 'configure', 'role': 'designate', 'fqdn_ip4': ['10.200.1.181'], 'username': 'root'}, 'designate-92e01ffc-4e96-5262-90d6-2f03ccd2feb1': {'id': 'designate-92e01ffc-4e96-5262-90d6-2f03ccd2feb1', 'osfinger': 'Ubuntu-22.04', 'uuid': '4a2a08cd-7ceb-4757-96a9-06b754f03878', 'build_phase': 'configure', 'role': 'designate', 'fqdn_ip4': ['10.200.1.178'], 'username': 'root'}, 'rabbitmq-1e969527-f30e-5db3-84f2-f6a4c9bf9796': {'id': 'rabbitmq-1e969527-f30e-5db3-84f2-f6a4c9bf9796', 'osfinger': 'Ubuntu-22.04', 'uuid': '1a2190e5-21fd-4ae1-9364-9aaf41d9e55a', 'build_phase': 'configure', 'role': 'rabbitmq', 'fqdn_ip4': ['10.200.1.157'], 'username': 'root'}, 'cache-4e6e6c67-e028-5d82-a00a-ea491241f875': {'id': 'cache-4e6e6c67-e028-5d82-a00a-ea491241f875', 'osfinger': 'Ubuntu-22.04', 'uuid': 'f4da82da-ab22-4ea0-bd10-4e73508b13d0', 'build_phase': 'configure', 'role': 'cache', 'fqdn_ip4': ['10.200.1.76'], 'username': 'root'}, 'placement-ab708fc3-c5c3-5238-9761-0a60b7caa1af': {'id': 'placement-ab708fc3-c5c3-5238-9761-0a60b7caa1af', 'osfinger': 'Ubuntu-22.04', 'uuid': 'b3abc9a8-4730-430c-a06f-a2375a8b7ad3', 'build_phase': 'configure', 'role': 'placement', 'fqdn_ip4': ['10.200.1.183'], 'username': 'root'}, 'mysql-f580011c-1d6e-5eb7-b635-7c1d7f2e6238': {'id': 'mysql-f580011c-1d6e-5eb7-b635-7c1d7f2e6238', 'osfinger': 'Ubuntu-22.04', 'uuid': 'a43bdf5f-aff5-4637-bba4-b68678d7b813', 'build_phase': 'configure', 'role': 'mysql', 'fqdn_ip4': ['10.200.1.56'], 'username': 'root'}, 'heat-2874605f-d5d6-5194-9f9e-bc03f742030c': {'id': 'heat-2874605f-d5d6-5194-9f9e-bc03f742030c', 'osfinger': 'Ubuntu-22.04', 'uuid': 'f7ccd2f4-7b6d-402f-9bd4-7a950fa40b87', 'build_phase': 'configure', 'role': 'heat', 'fqdn_ip4': ['10.200.1.174'], 'username': 'root'}, 'controller-d59eea19-1dd9-5012-bb2a-174d51ab291e': {'id': 'controller-d59eea19-1dd9-5012-bb2a-174d51ab291e', 'osfinger': 'Ubuntu-22.04', 'uuid': '35c13800-872f-11eb-8000-3cecef4bb0bc', 'build_phase': 'configure', 'role': 'controller', 'fqdn_ip4': ['10.200.1.55'], 'username': 'root'}, 'glance-bf3e1c1c-ebc4-55d5-9b19-7deaac76ce2c': {'id': 'glance-bf3e1c1c-ebc4-55d5-9b19-7deaac76ce2c', 'osfinger': 'Ubuntu-22.04', 'uuid': '8ac2edea-3320-4424-8276-00a7781ed4b5', 'build_phase': 'configure', 'role': 'glance', 'fqdn_ip4': ['10.200.1.190'], 'username': 'root'}, 'nova-c8bc45c4-038d-54b9-bad5-2ef34bfcde81': {'id': 'nova-c8bc45c4-038d-54b9-bad5-2ef34bfcde81', 'osfinger': 'Ubuntu-22.04', 'uuid': '159b67cf-c6ae-4a78-908f-3754ecb0ecce', 'build_phase': 'configure', 'role': 'nova', 'fqdn_ip4': ['10.200.1.191'], 'username': 'root'}, 'volume-89bac026-a520-519f-a300-4e98518a1a62': {'id': 'volume-89bac026-a520-519f-a300-4e98518a1a62', 'osfinger': 'Ubuntu-22.04', 'uuid': '6de7f278-3e02-4af8-8a54-1d88532cb056', 'build_phase': 'configure', 'role': 'volume', 'fqdn_ip4': ['10.200.1.198'], 'username': 'root'}, 'haproxy-d83f8f09-09d0-5823-ae12-25ab14707223': {'id': 'haproxy-d83f8f09-09d0-5823-ae12-25ab14707223', 'osfinger': 'Ubuntu-22.04', 'uuid': '39d3d828-1a11-417b-824f-1a9e907d5774', 'build_phase': 'configure', 'role': 'haproxy', 'fqdn_ip4': ['10.200.1.113'], 'username': 'root'}}