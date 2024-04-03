# """
# Connects to saltamole using the configuration specified in the 'config.yaml' file.
# """

# import requests
# from yaml import safe_load
# from range_monitor.db import get_db

# def read_config():
#     """
#     Reads the 'config.yaml' file and returns the loaded configuration.

#     Returns:
#         The loaded configuration as a dictionary.

#     Raises:
#         FileNotFoundError: If the 'config.yaml' file is not found.
#     """
#     try:
#         with open('clouds.yaml', 'r', encoding='utf-8') as config_file:
#             config = safe_load(config_file)
#     except FileNotFoundError as error:
#         raise FileNotFoundError('clouds.yaml file not found') from error

#     return config


# def salt_connect():
#     """
#     Connects to Salt using the configuration specified in the 'config.yaml' file.

#     Returns:
#         sconn (salt_connection): The connection object to Salt.
#     """

#     config = read_config()
#     if config:
#         salt_config = config['clouds']['saltamole']
#     else:
#         db = get_db()
#         salt_config_list = db.execute(
#             'SELECT p.*'
#             ' FROM saltamole p'
#             ' ORDER BY p.id'
#         ).fetchall()

#         salt_config = {
#             key: entry[key]
#             for entry in salt_config_list
#             for key in entry.keys()
#         }

#     sconn = session(salt_config['endpoint'],
#                     salt_config['datasource'],
#                     salt_config['username'],
#                     salt_config['password'])

#     return sconn


# def api_request(url, method='GET', data=None, headers=None):
#     """
#     Sends a request to the specified URL using the specified HTTP method
#     and optional data and headers.
    
#     Parameters:
#         url (str): The URL to send the request to.
#         method (str, optional): The HTTP method to use for the request. Defaults to 'GET'.
#         data (dict, optional): The data to include in the request body. Defaults to None.
#         headers (dict, optional): The headers to include in the request. Defaults to None.
        
#     Returns:
#         dict or None: The JSON response if the request was successful (status code 200)
#         otherwise None.
#     """
#     resp = requests.request(method,
#                             url,
#                             data=data,
#                             headers=headers,
#                             verify=False,
#                             timeout=5)
#     if resp.status_code == 200:
#         return resp.json()

#     return None

# # Example usage
# URL = 'http://salt-master.example.com:8000/run'
# METHOD = 'POST'
# DATA = {
#     'client': 'local',
#     'tgt': 'minion-id',
#     'fun': 'test.ping'
# }

# # response = api_request(URL, METHOD, DATA)
# # if response:
# #     print(response)
# # else:
# #     print('Request failed')
