

# from datetime import timedelta
# import guacamole


# CONNECTION_TIMEOUT = int(timedelta(minutes=5).total_seconds())


# # WORK IN PROGRESS

# class GuacamoleSessionService:
#     def __init__(self, guac_session: guacamole.session) -> None:
#         self.conn: guacamole.session = guac_session

#     def get_token(self) -> str:
#         return self.conn.token  # type: ignore

#     def active_identifiers(self) -> set[str]:
#         active_connections: dict[str, dict[str, str]] = self.conn.list_active_connections()  # type: ignore
#         return {conn['connectionIdentifier'] for conn in active_connections.values()}

#     def active_connections(self) -> None:
#         all_connections: dict = self.conn.list_connections()  # type: ignore

#         connection_ids = all_connections.keys()

#         active_conn_data = []
#         # type: ignore
#         active_conns: dict[str, dict] = self.conn.list_active_connections()

#         for active_conn in active_conns.values():
#             current_id: str | None = active_conn.get('connectionIdentifier')
#             if not current_id or not current_id in connection_ids:
#                 continue

#             conn_data: dict | None = all_connections.get(current_id)
#             if not conn_data:
#                 continue
#             connection_data = {
#                 'connection': conn_data.get('name'),
#                 'username': active_conn.get('username'),
#             }
#             active_conn_data.append(connection_data)
