

from range_monitor.guac.schema import ConnectionLabel, ConnectionWeight, TopologyModel


def get_node_weight(data: dict) -> ConnectionWeight:
    '''
    Not used, if you ever use the recursive tree response,
    this was the old way of determining the weight of a node

    Parameters
    ----------
    data : dict
    '''
    identifier = data['identifier']
    if identifier == 'ROOT':
        return ConnectionWeight.ROOT

    elif data.get('type'):
        return ConnectionWeight.GROUP

    elif int(data.get('activeConnections', 0)) > 0:
        return ConnectionWeight.ACTIVE_CONNECTION

    else:
        return ConnectionWeight.CONNECTION

def create_connection_label(
    data: dict,
    *,
    weight: ConnectionWeight | None = None
) -> ConnectionLabel:
    active_count = int(data.get('activeConnections', 0))

    if weight is None:
        weight = (
            ConnectionWeight.CONNECTION
            if active_count < 1
            else ConnectionWeight.ACTIVE_CONNECTION
        )

    return ConnectionLabel(
        identifier=data['identifier'],
        name=data['name'],
        parent_identifier=data.get('parentIdentifier'),
        weight=weight,
        active_connections=active_count
    )



def build_labels(
    topology: TopologyModel,
    *,
    connection_groups: dict,
    connections: dict,
) -> None:
    '''
    Populate the `nodes` field of a TopologyModel from the
    API responses of connection groups and connections.

    Parameters
    ----------
    topology : TopologyModel
        The topology model to populate
    connection_groups : dict
        The connection groups, keyed by identifier
    connections : dict
        The connections, keyed by identifier
    '''
    for id, data in connection_groups.items():
        topology.groups[id] = create_connection_label(
            data,
            weight=ConnectionWeight.GROUP
        )


    for id, data in connections.items():
        label = create_connection_label(data)
        topology.connections[id] = label
        topology.total_active += label.active_connections

    topology.total_labels = len(topology.connections) + len(topology.groups)


def create_root_label(data: dict, hostname: str) -> ConnectionLabel:
    data.update({
        'name': hostname,
        'identifier': 'ROOT',
        'parentIdentifier': None,
    })

    return create_connection_label(
        data,
        weight=ConnectionWeight.ROOT
    )




def create_group_topology(
    group_id: str,
    *,
    group_data: dict[str, dict],
    connections: dict
) -> TopologyModel | None:

    if not (group_dict := group_data.get(group_id)):
        return None

    root_label = create_root_label(
        data=group_dict,
        hostname=group_dict['name']
    )
    topology = TopologyModel(
        root=root_label
    )

    stack = [group_id]

    required_parent_ids = set()


    while stack:
        current_id = stack.pop()
        required_parent_ids.add(current_id)

        for id, data in group_data.items():
            if data.get('parentIdentifier', '_') != current_id:
                continue
            topology.groups[id] = create_connection_label(
                data,
                weight=ConnectionWeight.GROUP
            )
            stack.append(id)

    for id, data in connections.items():
        parent_id = data.get('parentIdentifier')
        if parent_id not in required_parent_ids:
            continue
        label = create_connection_label(data)
        topology.connections[id] = label
        topology.total_active += label.active_connections

