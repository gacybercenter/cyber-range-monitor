/* guac.static/topology/api_data.js */
import { hashDump } from "./hash_data.js";

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
    this.size = Math.pow(2, weight) + 1;
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
export class GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - guacamole.nodes[k] object
   */
  constructor(rawJson) {
    this.initialize(rawJson);
  }
  /**
   * a single entry in the api.nodes 
   * @param {Object} rawJson 
   */
  initialize(rawJson) {
    this.dump = rawJson;
    this._hash = hashDump(this.dump);
    this.identifier = rawJson.identifier;
    this.parentIdentifier = rawJson.parentIdentifier;
    this.name = rawJson.name ?? "Unknown";
    this.attributes = rawJson.attributes;
    this.activeConnections = rawJson.activeConnections || 0;
    this.type = rawJson.type ?? "Endpoint";
    this.positionKey = `${this.identifier}-${this.type}`;
  }

  getHash() {
    return this._hash;
  }

  /**
   * Replaces null or empty string attributes with "Not Set".
   * @returns {Object} The processed attributes.
   */
  stringifyAttributes() {
    const keys = Object.keys(this.attributes);
    if (keys.length === 0) {
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
  equals(otherDump) {
    const otherHash = hashDump(otherDump);
    return this.getHash() === otherHash;
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
 * @description
 * Represents a group of connections denoted in the JSON
 * or "dump" by having a type property and can have child
 * nodes or connections.
 * @property {string} type - The type of the connection group.
 * @property {number} weight - The weight of the connection group.
 * @property {NodeConfig} config - The styling configuration of the node.
 * @property {Map<string, string>} outgoingEdges - The outgoing edges of the connection group.
 */
export class ConnectionGroup extends GuacNode {
  initialize(rawJson) {
    super.initialize(rawJson);
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
    if (node.parentIdentifier !== this.identifier) {
      console.log("Why are you adding an edge to a node that isn't a child?");
      return;
    }
    this.outgoingEdges.set(this.identifier, node.identifier);
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
 * @description
 * Represents a single endpoint in the topology denoted by having
 * a protocol field in the JSON. An endpoint is a single connection
 * and is a leaf node in the topology
 * @property {string} type -
 * The type of the endpoint which is null in the json
 * but in the class it is set as ("Endpoint").
 * @property {string} protocol - The protocol used by the endpoint.
 * @property {number} weight - The weight of the endpoint based on its
 * active connections (check enums).
 * @property {NodeConfig} config - The styling configuration of the node
 * for how it will be rendered based on it's weight.
 * @property {number|string} lastActive - The last active timestamp or "Unknown"
 * (unix epoch).
 * @property {Array<Object>} sharingProfiles - The sharing profiles
 * associated with the endpoint, is null more often than not.
 * @property {Array<Object>} users - The users associated with the endpoint.
 */
export class GuacEndpoint extends GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - The raw JSON data representing the endpoint.
   */
  initialize(rawJson) {
    super.initialize(rawJson);
    this.type = "Endpoint";
    this.protocol = rawJson.protocol;
    this.setWeight();
    this.config = new NodeConfig(this.weight);
    this.lastActive = rawJson.lastActive ?? "Unknown";
    this.sharingProfiles = rawJson.sharingProfiles ?? [];
    this.users = rawJson.users;
  }


  /**
   * updates the weight and configuration based on the current active connections.
   */
  setWeight() {
    this.weight = this.isActive()
      ? NodeWeight.ACTIVE_ENDPOINT
      : NodeWeight.INACTIVE_ENDPOINT;

    if (!this.config) {
      this.config = new NodeConfig(this.weight);
      return;
    }

    this.config.update(this.weight);
  }
}

/**
 * @class GuacContext
 * @description
 * Manages the state of the topology and holds
 * the responsibility of updating the state of the
 * topology.
 * @property {Map<string, GuacNode>} nodeMap - Maps node identifiers to node instances.
 * @property {GuacNode[]} guacNodes - List of all nodes both Connection and Endpoints.
 * @property {ConnectionGroup[]} groups - The known group identifiers.
 * @property {Map<string, string>} edges - edges between nodes for graph generation.
 */
export class GuacContext {
  /**
   * @constructor
   */
  clearContext() {
    this.edges = [];
    this.groups = [];
    this.guacNodes = [];
    this.nodeMap = new Map();
  }
  constructor() {
    this.clearContext();
  }
  /**
   * sets the properties of the context
   * @param {Array<Object>} nodeData - The array of raw node JSON data.
   */
  buildContext(nodeData) {
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
    
    if(node.identifier === "ROOT" || node.type) {
      output = new ConnectionGroup(node);
      this.groups.push(output);
    } 
    if(node.protocol) {
      output = new GuacEndpoint(node);
    }
    
    if(!output) return;

    if (output.parent()) {      
      this.edges.push({
        source: output.parent(),
        target: output.identifier,
      });
    }
    this.guacNodes.push(output);
    this.nodeMap.set(output.identifier, output);
  }

  /**
   * @description
   * Accepts new data returned by Guac API
   * updates it and returns a boolean whether
   * or not the UI should change
   * @param {Object[]} nodeData
   * @returns {boolean}
   */
  hasChanged(nodeData) {
    if(nodeData.length !== this.guacNodes.length) {
      return true;
    }
    const newHashes = nodeData.map((node) => hashDump(node));
    const oldHashes = this.guacNodes.map((node) => node.getHash());
    return newHashes.some((hash, i) => hash !== oldHashes[i]);
  }
  shrinkEndpointNames() {
    const endpoints = this.getEndpoints();
    endpoints.forEach((endpoint) => {
      let parent = this.groups.find(
        (group) => group.identifier === endpoint.parentIdentifier
      );
      let parentName = parent.name;
      let parentWords = parentName.split(/[^a-zA-Z0-9]+/);
      parentWords.forEach((word) => {
        if (endpoint.name.includes(word)) {
          endpoint.name = endpoint.name.replace(word, "");
        }
      });
      endpoint.name = endpoint.name.replace(/^[^a-zA-Z0-9]+/, "");
    });
  }

  /**
   * given a parent id of a connection
   * group it will build a "mini" topology
   * using the outgoingEdges property of
   * connection group
   * @param {string} parentId
   * @returns {void}
   */
  buildGroupTopology(parentId) {
    const connGroup = this.getNode(parentId);

    if (!connGroup) return false;

    const children = this.filterBy((node) => node.parent() === parentId);
    children.forEach((child) => {
      connGroup.addEdge(child);
    });
    return true;
  }

  contains(nodeIdentifier) {
    return this.nodeMap.has(nodeIdentifier);
  }
  getNode(nodeIdentifier) {
    return this.nodeMap.get(nodeIdentifier);
  }

  /**
   * Finds all connection groups that satisfy the provided predicate.
   * @param {Function} predicate - The function to test each connection group.
   * @returns {ConnectionGroup[]} The array of connection groups that match the predicate.
   */
  filterBy(predicate) {
    return this.guacNodes.filter(predicate);
  }

  /**
   * retrieves all nodes in the context.
   * @returns {IterableIterator<GuacNode>}
   */
  getNodes() {
    return this.guacNodes;
  }
  getEndpoints() {
    return this.filterBy((node) => node instanceof GuacEndpoint);
  }
}
