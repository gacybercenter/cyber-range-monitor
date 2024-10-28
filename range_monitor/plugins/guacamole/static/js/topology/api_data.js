/* guac.static/topology/api_data.js */

/**
 * @enum {number} NodeWeight
 * @description Defines the weight categories for nodes.
 */
const NodeWeight = Object.freeze({
  ROOT: 5,
  GUAC_GROUP: 4,
  ACTIVE_ENDPOINT: 3,
  INACTIVE_ENDPOINT: 2,
  DEFAULT: 1,
});

/**
 * @enum {string} colors
 * @description  the colors associated with each node weight.
 */
const colors = Object.freeze({
  [NodeWeight.DEFAULT]: "rgb(0, 0, 0)", // black
  [NodeWeight.INACTIVE_ENDPOINT]: "rgb(192, 0, 0)", // red
  [NodeWeight.ACTIVE_ENDPOINT]: "rgb(0, 192, 0)", // green
  [NodeWeight.GUAC_GROUP]: "rgb(0, 0, 192)", // blue
  [NodeWeight.ROOT]: "rgb(255, 255, 255)", // white
});
const icons = Object.freeze({
  [NodeWeight.ACTIVE_ENDPOINT]: "endpoint.png",
  [NodeWeight.INACTIVE_ENDPOINT]: "inactive.png",
  [NodeWeight.ROOT]: "root.png",
  [NodeWeight.GUAC_GROUP]: "conn-group.png",
  [NodeWeight.DEFAULT]: "default.png",
});
/**
 * @class NodeConfig
 * @description Defines the styling configuration for a node.
 * @property {number} size - The size of the node.
 * @property {string} color - The fill color of the node.
 */
class NodeConfig {
  /**
   * @constructor
   * @param {number} weight - The weight of the node.
   */
  constructor(weight) {
    this.update(weight);
  }

  /**
   * @param {number} weight - The new weight of the node.
   */
  update(weight) {
    this.size = Math.pow(1.5, weight) + 1;
    this.color = colors[weight] || colors[NodeWeight.DEFAULT];
  }
}

/**
 * @class GuacNode
 * @description generalized information about nodes returned by the API
 * @property {Object} dump - The raw JSON data representing the node.
 * @property {string} identifier - Unique ID of the node.
 * @property {string} parentIdentifier - Identifier of the parent node.
 * @property {string} name - Name used for the node's label.
 * @property {Object} attributes - Key-value pairs of node attributes.
 * @property {number} activeConnections - Number of active connections for the node.
 */
class GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - guacamole.nodes[k] object
   */
  constructor(rawJson) {
    this.dump = rawJson;
    this.identifier = rawJson.identifier;
    this.parentIdentifier = rawJson.parentIdentifier ?? "Unknown";

    this.name = rawJson.name ?? "Unknown";
    this.attributes = rawJson.attributes;
    this.activeConnections = rawJson.activeConnections || 0;
  }

  /**
   * Replaces null or empty string attributes with "Not Set".
   * @returns {Object} The processed attributes.
   */
  getAttributeDisplay() {
    const keys = Object.keys(this.attributes);
    if(keys.length === 0) {
      return "No attributes set";
    }
    const displayable = {};
    keys.forEach((key) => {
      let cur = this.attributes[key];
      if (cur === null || cur === "") {
        displayable[key] = "Not Set";
      }
    });
    return displayable;
  }

  /**
   * @param {string} propName - The name of the property to retrieve.
   * @returns {string} The value of the property or "Not Set" if undefined.
   */
  getProperty(propName) {
    if (!this.hasOwnProperty(propName)) {
      return null;
    } else if (propName === "attributes") {
      return this.getAttributeDisplay();
    }
    return this[propName] ?? "Not Set";
  }

  parent() {
    return this.parentIdentifier;
  }

  isActive() {
    return this.activeConnections > 0;
  }
}

/**
 * @class ConnectionGroup
 * @extends GuacNode
 * @description Represents a group of connections.
 * @property {string} type - The type of the connection group.
 * @property {number} weight - The weight of the connection group.
 * @property {NodeConfig} config - The styling configuration of the node.
 * @property {Map<string, string>} outgoingEdges - The outgoing edges of the connection group.
 */
class ConnectionGroup extends GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - The raw JSON data representing the connection group.
   */
  constructor(rawJson) {
    super(rawJson);
    this.type = rawJson.type;
    this.setWeight();
    this.config = new NodeConfig(this.weight);
    this.outgoingEdges = new Map();
  }

  /**
   * Sets the weight of the connection group based on its identifier.
   */
  setWeight() {
    if (this.identifier === "ROOT") {
      this.weight = NodeWeight.ROOT;
    } else {
      this.weight = NodeWeight.GUAC_GROUP;
    }
  }

  /**
   * Adds an outgoing edge to the connection group.
   * @param {GuacNode} node - The target node to connect to.
   */
  addEdge(node) {
    this.outgoingEdges.set(node.identifier, node.identifier);
  }

  /**
   * Removes an outgoing edge from the connection group.
   * @param {GuacNode} node - The target node to disconnect from.
   */
  removeEdge(node) {
    this.outgoingEdges.delete(node.identifier);
  }

  /**
   * Retrieves all outgoing edges.
   * @returns {Map<string, string>} The outgoing edges.
   */
  edges() {
    return this.outgoingEdges;
  }
}

/**
 * @class GuacEndpoint
 * @extends GuacNode
 * @description Represents an endpoint in the topology.
 * @property {string} type - The type of the endpoint ("Endpoint").
 * @property {string} protocol - The protocol used by the endpoint.
 * @property {number} weight - The weight of the endpoint based on its active connections.
 * @property {NodeConfig} config - The styling configuration of the node.
 * @property {number|string} lastActive - The last active timestamp or "Unknown".
 * @property {Array<Object>} sharingProfiles - The sharing profiles associated with the endpoint.
 * @property {Array<Object>} users - The users associated with the endpoint.
 * @method updateWeight - Updates the weight and configuration based on active connections.
 */
class GuacEndpoint extends GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - The raw JSON data representing the endpoint.
   */
  constructor(rawJson) {
    super(rawJson);
    this.type = "Endpoint";
    this.protocol = rawJson.protocol ?? "N/A";

    this.weight = this.isActive()
      ? NodeWeight.ACTIVE_ENDPOINT
      : NodeWeight.INACTIVE_ENDPOINT;

    this.config = new NodeConfig(this.weight);

    this.lastActive = rawJson.lastActive ?? "Unknown";
    this.sharingProfiles = rawJson.sharingProfiles ?? [];
    this.users = rawJson.users ?? [];
  }

  /**
   * updates the weight and configuration based on the current active connections.
   */
  updateWeight() {
    this.weight = this.isActive()
      ? NodeWeight.ACTIVE_ENDPOINT
      : NodeWeight.INACTIVE_ENDPOINT;
    this.config.update(this.weight);
  }
}

/**
 * @class GuacContext
 * @description Holds all connection groups and endpoints.
 * @property {Map<string, GuacNode>} nodeMap - Maps node identifiers to node instances.
 * @property {ConnectionGroup[]} connGroups - The connection groups.
 * @property {GuacEndpoint[]} endpoints - The endpoints (non-connecting nodes).
 * @property {Set<string>} knownGroupIds - The known group identifiers.
 * @property {Map<string, string>} edges - The edges between nodes for graph generation.
 */
class GuacContext {
  /**
   * @constructor
   */
  constructor() {
    this.edges = new Map();
    this.nodeMap = new Map();
    this.knownGroupIds = new Set();

    this.connGroups = [];
    this.guacNodes = [];
  }
  endpoints() {
    return this.endpoints;
  }
  /**
   * Builds the context by processing the provided node data.
   * @param {Array<Object>} nodeData - The array of raw node JSON data.
   */
  buildContext(nodeData) {
    this.nodeMap = new Map(nodeData.map((node) => [node.identifier, node]));
    nodeData.forEach((node) => {
      this.addContext(node);
    });
  }

  /**
   * Adds a single node to the context, categorizing it as a ConnectionGroup or GuacEndpoint.
   * @param {Object} node - The raw node JSON data.
   */
  addContext(node) {
    let output;
    if (node.type && !this.knownGroupIds.has(node.identifier)) {
      output = new ConnectionGroup(node);
      this.connGroups.push(output);
      this.knownGroupIds.add(node.identifier);
    } else {
      output = new GuacEndpoint(node);
      this.handleNewEndpoint(output);
    }

    if (output.parent()) {
      this.edges.set(output.parent(), output.identifier);
    }
    this.guacNodes.push(output);
  }

  /**
   * Handles adding edges for a new endpoint,
   * ensuring the parent group exists before hand.
   * @param {GuacEndpoint} endpoint - The newly added endpoint.
   */
  handleNewEndpoint(endpoint) {
    const parentId = endpoint.parent();
    if (this.knownGroupIds.has(parentId)) {
      return;
    }
    // sanity check
    if (!this.nodeMap.has(parentId)) {
      return;
    }
    const parentJson = this.nodeMap.get(parentId);
    const connGroup = new ConnectionGroup(parentJson);
    connGroup.addEdge(endpoint);
    this.knownGroupIds.add(parentId);
    this.connGroups.push(connGroup);
  }

  /**
   * Checks if a node with the given identifier exists in the context.
   * @param {string} nodeIdentifier - The identifier of the node to check.
   * @returns {boolean} True if the node exists, else false.
   */
  contains(nodeIdentifier) {
    return this.nodeMap.has(nodeIdentifier);
  }

  /**
   * Retrieves a node by its identifier.
   * @param {string} nodeIdentifier - The identifier of the node to retrieve.
   * @returns {GuacNode|undefined} The node instance or undefined if not found.
   */
  getNode(nodeIdentifier) {
    return this.nodeMap.get(nodeIdentifier);
  }

  /**
   * Finds all connection groups that satisfy the provided predicate.
   * @param {Function} predicate - The function to test each connection group.
   * @returns {ConnectionGroup[]} The array of connection groups that match the predicate.
   */
  findAllBy(predicate) {
    return this.connGroups.filter(predicate);
  }

  /**
   * retrieves all nodes in the context.
   * @returns {IterableIterator<GuacNode>}
   */
  getNodes() {
    return this.guacNodes;
  }
  getEndpoints() {
    return this.guacNodes.filter(
      (node) => node instanceof GuacEndpoint
    );
  }
}



