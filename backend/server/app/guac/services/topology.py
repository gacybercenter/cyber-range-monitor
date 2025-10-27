import asyncio
from typing import NamedTuple

from server.app.errors.http import BadRequestError
from server.app.guac.client import operations
from server.app.guac.client.spec import GuacamoleAPISpec
from server.app.guac.schema import GuacNode, NodeWeight, TopologyModel


def _get_node_weight(data: dict) -> NodeWeight:
    '''
    Not used, if you ever use the recursive tree response,
    this was the old way of determining the weight of a node

    Parameters
    ----------
    data : dict
        The JSON data for the node
    Returns
    -------
    NodeWeight
    '''
    identifier = data['identifier']
    if identifier == 'ROOT':
        return NodeWeight.ROOT

    if data.get('type'):
        return NodeWeight.GROUP

    if int(data.get('activeConnections', 0)) > 0:
        return NodeWeight.ACTIVE_CONNECTION

    return NodeWeight.CONNECTION


def _create_guacnode(data: dict, *, weight: NodeWeight | None = None) -> GuacNode:
    '''
    Creates a GuacNode from the response data
    with an optional weight
    '''
    active_count = int(data.get('activeConnections', 0))

    if weight is None:
        weight = (
            NodeWeight.CONNECTION if active_count < 1 else NodeWeight.ACTIVE_CONNECTION
        )

    return GuacNode(
        identifier=data['identifier'],
        name=data['name'],
        parent_identifier=data.get('parentIdentifier'),
        weight=weight,
        active_connections=active_count,
    )


def _create_root(data: dict, hostname: str) -> GuacNode:
    data.update({
        'name': hostname,
        'identifier': 'ROOT',
        'parentIdentifier': None,
    })
    return _create_guacnode(data, weight=NodeWeight.ROOT)


def _get_related_connection_groups(
    group_id: str,
    *,
    bag: dict[str, GuacNode],
    group_json: dict[str, dict],
) -> set[str]:
    '''
    Gets all related connection group IDs for a specific group ID with
    using depth-first search on the group_json returned from `list_connection_groups`
    while populating the `bag` with GuacNode labels. bag should be `topology.groups`

    Parameters
    ----------
    group_id : str
        The group identifier to start from
    bag : dict[str, GuacNode]
        Where to put parsed GuacNode labels
    group_json : dict[str, dict]
        The JSON response from `list_connection_groups`

    Returns
    -------
    set[str]
    '''
    stack = [group_id]
    related_group_ids = set()

    while stack:
        current_id = stack.pop()
        related_group_ids.add(current_id)
        for id, json_data in group_json.items():
            if json_data.get('parentIdentifier', '_') != current_id:
                continue
            label = _create_guacnode(json_data, weight=NodeWeight.GROUP)
            bag[id] = label
            stack.append(id)

    return related_group_ids


class TopologyContext(NamedTuple):
    groups: dict[str, dict]
    connections: dict[str, dict]


async def fetch_topology_context(spec: GuacamoleAPISpec) -> TopologyContext:
    groups_resp, connections_resp = await asyncio.gather(
        operations.list_connection_groups(spec), operations.list_connections(spec)
    )

    return TopologyContext(groups=groups_resp or {}, connections=connections_resp or {})


class TopologyService:
    '''
    The service for building and retrieving Guacamole topologies.
    '''

    def __init__(self, spec: GuacamoleAPISpec) -> None:
        self.spec = spec

    async def get_root_topology(self) -> TopologyModel:
        '''
        Gets the full topology from the root group.

        Returns
        -------
        TopologyModel
        '''
        root_json = await operations.get_connection_group(self.spec, 'ROOT')
        root_label = _create_root(data=root_json, hostname=self.spec.base_url)
        topology = TopologyModel(root=root_label)
        context = await fetch_topology_context(self.spec)

        for id, data in context.groups.items():
            topology.groups[id] = _create_guacnode(data, weight=NodeWeight.GROUP)

        for id, data in context.connections.items():
            label = _create_guacnode(data)
            topology.connections[id] = label
            topology.total_active += label.active_connections

        topology.total_labels = len(topology.connections) + len(topology.groups)
        return topology

    async def get_group_topology(self, group_id: str) -> TopologyModel | None:
        '''
        Gets the topology for a specific connection group.

        Parameters
        ----------
        group_id : str
            The group identifier

        Returns
        -------
        TopologyModel | None
        '''
        context = await fetch_topology_context(self.spec)

        if not (root := context.groups.get(group_id)):  # if the group does not exist
            return None

        root_label = _create_root(data=root, hostname=root['name'])
        topology = TopologyModel(root=root_label)
        related_group_ids = _get_related_connection_groups(
            group_id, bag=topology.groups, group_json=context.groups
        )
        for id, data in context.connections.items():
            parent_id = data.get('parentIdentifier')
            if parent_id not in related_group_ids:
                continue
            label = _create_guacnode(data)
            topology.connections[id] = label
            topology.total_active += label.active_connections

        topology.total_labels = len(topology.connections) + len(topology.groups)
        return topology

    async def fetch(self, group_id: str | None = None) -> TopologyModel:
        '''
        Gets the full topology or a specific connection group topology.

        Parameters
        ----------
        group_id : str | None
            The identifier for the connection group to build the topology for.
            If None, builds the full topology from the root group.

        Returns
        -------
        TopologyModel
            The complete, organized topology with labels
            and weights for connections and groups.
        '''
        if not group_id:
            return await self.get_root_topology()

        if group_id == 'ROOT':
            return await self.get_root_topology()

        result = await self.get_group_topology(group_id)
        if result is None:
            raise BadRequestError('The specified connection group does not exist.')

        return result
