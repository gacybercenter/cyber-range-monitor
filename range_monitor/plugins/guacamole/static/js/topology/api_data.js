/* guac.static/topology/api_data.js */
import { hashDump } from './hash_data.js';

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
export class GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - guacamole.nodes[k] object
   */
  constructor(rawJson) {
    this.initialize(rawJson);
  }
  initialize(rawJson) {
    this._hash = hashDump(this.dump);
    this.dump = rawJson;

    this.identifier = rawJson.identifier;
    this.parentIdentifier = rawJson.parentIdentifier;

    this.name = rawJson.name ?? "Unknown";
    this.attributes = rawJson.attributes;
    this.activeConnections = rawJson.activeConnections || 0;
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


  /**
   * @param {string} propName - The name of the property to retrieve.
   * @returns {string} The value of the property or "Not Set" if undefined.
   */
  getProperty(propName) {
    if (!this.hasOwnProperty(propName)) {
      return "Not Set";
    } else if (propName === "attributes") {
      return this.stringifyAttributes();
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
export class ConnectionGroup extends GuacNode {
  initialize(rawJson) {
    super.initialize(rawJson);
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
export class GuacEndpoint extends GuacNode {
  /**
   * @constructor
   * @param {Object} rawJson - The raw JSON data representing the endpoint.
   */
  initialize(rawJson) {
    super.initialize(rawJson);
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
 * @property {ConnectionGroup[]} groups - The connection groups.
 * @property {Set<string>} knownGroupIds - The known group identifiers.
 * @property {Map<string, string>} edges - The edges between nodes for graph generation.
 */
export class GuacContext {
  /**
   * @constructor
   */
  constructor() {
    this.edges = new Map();
    this.nodeMap = new Map();
    this.groups = [];
    this.guacNodes = [];
  }
  /**
   * sets the properties of the context
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
    if (node.type) {
      output = new ConnectionGroup(node);
      this.groups.push(output);
    } else {
      output = new GuacEndpoint(node);
    }
    if (output.parent()) {
      this.edges.set(output.parent(), output.identifier);
    }
    this.guacNodes.push(output);
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

const sample = {
  nodes: [
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.106",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "8481",
      lastActive: 1713531405000,
      name: "gremoore-heat-workshop",
      parentIdentifier: "1851",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "true",
        "max-connections": "100",
        "max-connections-per-user": "100",
      },
      identifier: "1851",
      name: "interns",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.216",
        "guacd-port": null,
        "max-connections": null,
        "max-connections-per-user": null,
        weight: null,
      },
      identifier: "10122",
      lastActive: 1719867116000,
      name: "playground.kali.1",
      parentIdentifier: "2046",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "1629",
          name: "playground.kali.1.share",
          primaryConnectionIdentifier: "10122",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.216",
        "guacd-port": null,
        "max-connections": null,
        "max-connections-per-user": null,
        weight: null,
      },
      identifier: "10125",
      lastActive: 1721140134000,
      name: "playground.win11.1",
      parentIdentifier: "2046",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "1632",
          name: "playground.win11.1.share",
          primaryConnectionIdentifier: "10125",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2046",
      name: "playground",
      parentIdentifier: "2043",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2043",
      name: "cyber-range-testing",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "22911",
      lastActive: 1727121681000,
      name: "playground.server.win11",
      parentIdentifier: "2288",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "2288",
      name: "playground",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.168",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "17757",
      name: "gcr-ctf-dev.attack.kali.1",
      parentIdentifier: "2571",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3132",
          name: "gcr-ctf-dev.attack.kali.1.share",
          primaryConnectionIdentifier: "17757",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.168",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18711",
      name: "gcr-ctf-dev.ctfd.landing",
      parentIdentifier: "2571",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3162",
          name: "gcr-ctf-dev.ctfd.landing.share",
          primaryConnectionIdentifier: "18711",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.168",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18714",
      name: "gcr-ctf-dev.defend.kali.1",
      parentIdentifier: "2571",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3165",
          name: "gcr-ctf-dev.defend.kali.1.share",
          primaryConnectionIdentifier: "18714",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2571",
      name: "ctf-dev",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.127",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18432",
      lastActive: 1724245857000,
      name: "heatworkshop.workshop.user.1",
      parentIdentifier: "2700",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3135",
          name: "heatworkshop.workshop.user.1.share",
          primaryConnectionIdentifier: "18432",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2700",
      name: "heatworkshop",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18699",
      lastActive: 1723501835000,
      name: "automation.screen.server.3",
      parentIdentifier: "2775",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18702",
      lastActive: 1729863124000,
      name: "automation.screen.server.2",
      parentIdentifier: "2775",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18705",
      lastActive: 1723501815000,
      name: "automation.screen.server.4",
      parentIdentifier: "2775",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18708",
      lastActive: 1723582823000,
      name: "automation.screen.server.1",
      parentIdentifier: "2775",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2775",
      name: "automation",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.70",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18747",
      lastActive: 1723037319000,
      name: "workshop.attack.kali.10",
      parentIdentifier: "2802",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.70",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18750",
      lastActive: 1723056460000,
      name: "workshop.target.webserver.10",
      parentIdentifier: "2802",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.70",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "18753",
      lastActive: 1723036314000,
      name: "workshop.target.windows.10",
      parentIdentifier: "2802",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "2802",
      name: "workshop",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19590",
      lastActive: 1724777014000,
      name: "web-pod-test.haproxy.server",
      parentIdentifier: "2970",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.107",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19611",
      name: "web-pod-test.precheck.server",
      parentIdentifier: "2970",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.107",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19614",
      lastActive: 1724770590000,
      name: "web-pod-test.deepsurface.server",
      parentIdentifier: "2970",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.107",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19617",
      lastActive: 1724770594000,
      name: "web-pod-test.wazuh.server",
      parentIdentifier: "2970",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.107",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19620",
      name: "web-pod-test.monitor.server",
      parentIdentifier: "2970",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "20",
        "max-connections-per-user": "10",
      },
      identifier: "2970",
      name: "web-pod-test",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.125",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19800",
      lastActive: 1726583523000,
      name: "augtech.win10.1",
      parentIdentifier: "2994",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3333",
          name: "augtech.win10.1.dev.share",
          primaryConnectionIdentifier: "19800",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.125",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19803",
      lastActive: 1726504533000,
      name: "augtech.win11.1",
      parentIdentifier: "2994",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3336",
          name: "augtech.win11.1.dev.share",
          primaryConnectionIdentifier: "19803",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.20.125",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19806",
      lastActive: 1726583793000,
      name: "augtech.kali.1",
      parentIdentifier: "2994",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3339",
          name: "augtech.kali.1.student.share",
          primaryConnectionIdentifier: "19806",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2994",
      name: "augtech",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19869",
      lastActive: 1727299351000,
      name: "persistent_fake_internet.internet.red.16.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19872",
      lastActive: 1727299698000,
      name: "persistent_fake_internet.internet.red.13.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19875",
      lastActive: 1727358194000,
      name: "persistent_fake_internet.internet.red.19.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19878",
      lastActive: 1727635783000,
      name: "persistent_fake_internet.internet.red.3.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19881",
      lastActive: 1729084584000,
      name: "persistent_fake_internet.internet.red.10.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19884",
      lastActive: 1727365659000,
      name: "persistent_fake_internet.internet.red.12.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19887",
      lastActive: 1727290801000,
      name: "persistent_fake_internet.internet.red.20.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19890",
      lastActive: 1727299831000,
      name: "persistent_fake_internet.internet.red.2.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19893",
      lastActive: 1727299276000,
      name: "persistent_fake_internet.internet.red.4.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19896",
      lastActive: 1727356434000,
      name: "persistent_fake_internet.internet.red.8.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19899",
      lastActive: 1727299096000,
      name: "persistent_fake_internet.internet.red.17.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19902",
      lastActive: 1727360814000,
      name: "persistent_fake_internet.internet.red.15.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19905",
      lastActive: 1727299396000,
      name: "persistent_fake_internet.internet.red.7.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19908",
      lastActive: 1727111918000,
      name: "persistent_fake_internet.internet.red.11.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19911",
      lastActive: 1728499131000,
      name: "persistent_fake_internet.internet.red.14.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19914",
      lastActive: 1727299576000,
      name: "persistent_fake_internet.internet.red.5.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19917",
      lastActive: 1727298931000,
      name: "persistent_fake_internet.internet.red.18.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19920",
      lastActive: 1728499101000,
      name: "persistent_fake_internet.internet.red.1.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19923",
      lastActive: 1727730826000,
      name: "persistent_fake_internet.internet.red.9.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19926",
      lastActive: 1727298885000,
      name: "persistent_fake_internet.internet.red.6.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19929",
      lastActive: 1726582758000,
      name: "persistent_fake_internet.internet.red.16.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19932",
      name: "persistent_fake_internet.internet.red.13.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19935",
      lastActive: 1726836319000,
      name: "persistent_fake_internet.internet.red.19.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19938",
      name: "persistent_fake_internet.internet.red.3.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19941",
      lastActive: 1726791564000,
      name: "persistent_fake_internet.internet.red.10.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19944",
      name: "persistent_fake_internet.internet.red.12.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19947",
      lastActive: 1726853104000,
      name: "persistent_fake_internet.internet.red.20.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19950",
      lastActive: 1724961023000,
      name: "persistent_fake_internet.internet.red.2.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19953",
      name: "persistent_fake_internet.internet.red.4.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19956",
      lastActive: 1724852351000,
      name: "persistent_fake_internet.internet.red.8.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19959",
      lastActive: 1727299201000,
      name: "persistent_fake_internet.internet.red.17.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19962",
      name: "persistent_fake_internet.internet.red.15.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19965",
      lastActive: 1726338142000,
      name: "persistent_fake_internet.internet.red.7.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19968",
      lastActive: 1727108800000,
      name: "persistent_fake_internet.internet.red.11.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19971",
      lastActive: 1727267852000,
      name: "persistent_fake_internet.internet.red.14.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19974",
      lastActive: 1725802026000,
      name: "persistent_fake_internet.internet.red.5.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19977",
      lastActive: 1727096520000,
      name: "persistent_fake_internet.internet.red.18.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19980",
      lastActive: 1726791563000,
      name: "persistent_fake_internet.internet.red.1.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19983",
      lastActive: 1727129945000,
      name: "persistent_fake_internet.internet.red.9.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "19986",
      lastActive: 1725970984000,
      name: "persistent_fake_internet.internet.red.6.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "23142",
      lastActive: 1727295930000,
      name: "persistent_fake_internet.internet.red.21.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "23145",
      name: "persistent_fake_internet.internet.red.22.ubuntu",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "23148",
      lastActive: 1728661800000,
      name: "persistent_fake_internet.internet.red.21.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "23151",
      lastActive: 1728660987000,
      name: "persistent_fake_internet.internet.red.22.kali",
      parentIdentifier: "2997",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.112",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24021",
      lastActive: 1728661227000,
      name: "persistent_fake_internet.internet.red.22.kali.ssh",
      parentIdentifier: "2997",
      protocol: "ssh",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "2997",
      name: "persistent_fake_internet",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20655",
      lastActive: 1729727150000,
      name: "CFIC-ZeroDay.attack.kali.2",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20658",
      lastActive: 1729863393000,
      name: "CFIC-ZeroDay.attack.kali.4",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20661",
      lastActive: 1729863378000,
      name: "CFIC-ZeroDay.attack.kali.3",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20664",
      lastActive: 1729850533000,
      name: "CFIC-ZeroDay.attack.kali.1",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20955",
      lastActive: 1729863390000,
      name: "CFIC-ZeroDay.attack.kali.7",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": null,
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20958",
      lastActive: 1727381244000,
      name: "CFIC-ZeroDay.win11",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20961",
      lastActive: 1729744620000,
      name: "CFIC-ZeroDay.attack.kali.5",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20964",
      lastActive: 1729863390000,
      name: "CFIC-ZeroDay.attack.kali.6",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.95",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "20997",
      lastActive: 1729884569000,
      name: "CFIC-ZeroDay.attack.kali.8",
      parentIdentifier: "3069",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "50",
        "max-connections-per-user": "10",
      },
      identifier: "3069",
      name: "CFIC-ZeroDay",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.146",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "21003",
      lastActive: 1729516590000,
      name: "ncae-koth.attack.1.kali.1",
      parentIdentifier: "3147",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3462",
          name: "ncae-koth.attack.1.kali.1.share",
          primaryConnectionIdentifier: "21003",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.146",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "21096",
      lastActive: 1728660147000,
      name: "ncae-koth.attack.1.kali.5",
      parentIdentifier: "3147",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3489",
          name: "ncae-koth.attack.1.kali.5.share",
          primaryConnectionIdentifier: "21096",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.146",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "21099",
      name: "ncae-koth.attack.1.kali.4",
      parentIdentifier: "3147",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3492",
          name: "ncae-koth.attack.1.kali.4.share",
          primaryConnectionIdentifier: "21099",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.146",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "21102",
      lastActive: 1728672702000,
      name: "ncae-koth.attack.1.kali.3",
      parentIdentifier: "3147",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3495",
          name: "ncae-koth.attack.1.kali.3.share",
          primaryConnectionIdentifier: "21102",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.146",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "21105",
      lastActive: 1729256015000,
      name: "ncae-koth.attack.1.kali.2",
      parentIdentifier: "3147",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "3498",
          name: "ncae-koth.attack.1.kali.2.share",
          primaryConnectionIdentifier: "21105",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "3147",
      name: "ncae-koth.1",
      parentIdentifier: "3144",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.102",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24102",
      name: "ncae-koth.attack.2.kali.5",
      parentIdentifier: "3237",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5193",
          name: "ncae-koth.attack.2.kali.5.share",
          primaryConnectionIdentifier: "24102",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.102",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24105",
      name: "ncae-koth.attack.2.kali.1",
      parentIdentifier: "3237",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5196",
          name: "ncae-koth.attack.2.kali.1.share",
          primaryConnectionIdentifier: "24105",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.102",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24108",
      name: "ncae-koth.attack.2.kali.4",
      parentIdentifier: "3237",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5199",
          name: "ncae-koth.attack.2.kali.4.share",
          primaryConnectionIdentifier: "24108",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.102",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24111",
      name: "ncae-koth.attack.2.kali.3",
      parentIdentifier: "3237",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5202",
          name: "ncae-koth.attack.2.kali.3.share",
          primaryConnectionIdentifier: "24111",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.22.102",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24114",
      name: "ncae-koth.attack.2.kali.2",
      parentIdentifier: "3237",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5205",
          name: "ncae-koth.attack.2.kali.2.share",
          primaryConnectionIdentifier: "24114",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "3237",
      name: "ncae-koth.2",
      parentIdentifier: "3144",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "3144",
      name: "ncae-koth",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.28",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24000",
      lastActive: 1729016107000,
      name: "ncae-day1-test.day1.analyst.1",
      parentIdentifier: "3225",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5109",
          name: "ncae-day1-test.day1.analyst.1.share",
          primaryConnectionIdentifier: "24000",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.28",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24012",
      lastActive: 1729016077000,
      name: "ncae-day1-test.day1.kali.1",
      parentIdentifier: "3225",
      protocol: "rdp",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.28",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24015",
      lastActive: 1729000492000,
      name: "ncae-day1-test.day1.analyst.2",
      parentIdentifier: "3225",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5115",
          name: "ncae-day1-test.day1.analyst.2.share",
          primaryConnectionIdentifier: "24015",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.23.28",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24018",
      lastActive: 1729018777000,
      name: "ncae-day1-test.day1.kali.2",
      parentIdentifier: "3225",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5118",
          name: "ncae-day1-test.day1.kali.2.share",
          primaryConnectionIdentifier: "24018",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "3225",
      name: "ncae-day1-test",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24024",
      lastActive: 1728916692000,
      name: "ncae-day1.day1.analyst.1",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5121",
          name: "ncae-day1.day1.analyst.1.share",
          primaryConnectionIdentifier: "24024",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24027",
      lastActive: 1728930807000,
      name: "ncae-day1.day1.kali.1",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5124",
          name: "ncae-day1.day1.kali.1.share",
          primaryConnectionIdentifier: "24027",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24030",
      lastActive: 1728916167000,
      name: "ncae-day1.day1.analyst.2",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5127",
          name: "ncae-day1.day1.analyst.2.share",
          primaryConnectionIdentifier: "24030",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24033",
      lastActive: 1729025392000,
      name: "ncae-day1.day1.kali.2",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5130",
          name: "ncae-day1.day1.kali.2.share",
          primaryConnectionIdentifier: "24033",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24036",
      lastActive: 1728916119000,
      name: "ncae-day1.day1.analyst.3",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5133",
          name: "ncae-day1.day1.analyst.3.share",
          primaryConnectionIdentifier: "24036",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24039",
      lastActive: 1728916152000,
      name: "ncae-day1.day1.analyst.4",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5136",
          name: "ncae-day1.day1.analyst.4.share",
          primaryConnectionIdentifier: "24039",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24042",
      lastActive: 1729178617000,
      name: "ncae-day1.day1.analyst.5",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5139",
          name: "ncae-day1.day1.analyst.5.share",
          primaryConnectionIdentifier: "24042",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24045",
      name: "ncae-day1.day1.kali.3",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5142",
          name: "ncae-day1.day1.kali.3.share",
          primaryConnectionIdentifier: "24045",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24048",
      name: "ncae-day1.day1.kali.4",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5145",
          name: "ncae-day1.day1.kali.4.share",
          primaryConnectionIdentifier: "24048",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.250",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24051",
      name: "ncae-day1.day1.kali.5",
      parentIdentifier: "3228",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5148",
          name: "ncae-day1.day1.kali.5.share",
          primaryConnectionIdentifier: "24051",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "3228",
      name: "ncae-day1",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24081",
      lastActive: 1729617538000,
      name: "ncae-red-test.kali.1",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5172",
          name: "ncae-red-test.kali.1.share",
          primaryConnectionIdentifier: "24081",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24084",
      name: "ncae-red-test.kali.2",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5175",
          name: "ncae-red-test.kali.2.share",
          primaryConnectionIdentifier: "24084",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24087",
      name: "ncae-red-test.kali.3",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5178",
          name: "ncae-red-test.kali.3.share",
          primaryConnectionIdentifier: "24087",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24090",
      name: "ncae-red-test.kali.4",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5181",
          name: "ncae-red-test.kali.4.share",
          primaryConnectionIdentifier: "24090",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24093",
      lastActive: 1729185545000,
      name: "ncae-red-test.kali.5",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5184",
          name: "ncae-red-test.kali.5.share",
          primaryConnectionIdentifier: "24093",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24096",
      lastActive: 1729107234000,
      name: "ncae-red-test.engineer.server",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5187",
          name: "ncae-red-test.engineer.server.share",
          primaryConnectionIdentifier: "24096",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "failover-only": null,
        "guacd-encryption": null,
        "guacd-hostname": "10.101.21.56",
        "guacd-port": null,
        "max-connections": "1",
        "max-connections-per-user": "1",
        weight: null,
      },
      identifier: "24099",
      lastActive: 1729863852000,
      name: "ncae-red-test.scs.workstation",
      parentIdentifier: "3234",
      protocol: "rdp",
      sharingProfiles: [
        {
          attributes: {},
          identifier: "5190",
          name: "ncae-red-test.scs.workstation.share",
          primaryConnectionIdentifier: "24099",
        },
      ],
    },
    {
      activeConnections: 0,
      attributes: {
        "enable-session-affinity": "",
        "max-connections": "200",
        "max-connections-per-user": "10",
      },
      identifier: "3234",
      name: "ncae-red-test",
      parentIdentifier: "ROOT",
      type: "ORGANIZATIONAL",
    },
    {
      activeConnections: 0,
      attributes: {},
      identifier: "ROOT",
      name: "https://training.gacyberrange.org",
      type: "ORGANIZATIONAL",
    },
  ],
};
