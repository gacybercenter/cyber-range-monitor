# Guacamole Monitor

The Guacamole Monitor is web-based application that for monitoring and
interacting with a Guacamole server.

## Features

The Guacamole Monitor allows the user to visualize and interact with
Guacamole connections.

**Topology**  
- View all connections in an interactive topology
    - Zoom, drag, and select nodes
- Connect to selected nodes
    - If there is an active connection, connect via active connection
- Kill selected node connections.
- Updates every 5 seconds

**Active Connections**  
- View active connections and their associated users
    - Separated by connection organization

**Active Users**  
- View active users
    - Separated by guacamole organization

## Requirements
To ensure proper functionality and usage, identified below is the baseline
directory structure and required for use of Guacamole Monitor.

**Project Repository Structure**  
```shell
DIR
|___ config.yaml
```

### **Guacamole Configuration Template** 

_Expected parameters within the `config.yaml`_
```yaml
guacamole:
  host: https://guacamole.host.org
  data_source: mysql
  username: admin
  password: password123
```