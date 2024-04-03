# """
# Helper functions
# """

# def extract_connections(obj: dict) -> (list, dict):
#     """
#     Recursively walks through an object and extracts connection groups,
#     connections, and sharing groups.

#     Parameters:
#     obj (dict): The object to extract groups and connections from.

#     Returns:
#     list: The extracted connection groups, connections, and sharing groups.
#     """

#     conns = []

#     if isinstance(obj, dict):
#         if obj.get('name') and obj.get('parentIdentifier'):
#             conn = obj.copy()
#             if conn.get('childConnectionGroups'):
#                 del conn['childConnectionGroups']
#             if conn.get('childConnections'):
#                 del conn['childConnections']
#             conns.append(conn)

#         for value in obj.values():
#             if isinstance(value, (dict, list)):
#                 child_conns = extract_connections(value)
#                 conns.extend(child_conns)

#     elif isinstance(obj, list):
#         for item in obj:
#             if isinstance(item, (dict, list)):
#                 child_conns = extract_connections(item)
#                 conns.extend(child_conns)

#     return conns


# def remove_empty(obj: object) -> object:
#     """
#     Recursively removes None and empty values from a dictionary or a list.

#     obj:
#     dictionary (dict or list): The dictionary or list to remove None and empty values from.

#     Returns:
#     dict or list: The dictionary or list with None and empty values removed.
#     """
#     if isinstance(obj, dict):
#         return {
#             key: remove_empty(value)
#             for key, value in obj.items()
#             if value
#         }
#     if isinstance(obj, list):
#         return [
#             remove_empty(item)
#             for item in obj
#             if item
#         ]

#     return obj
# # 