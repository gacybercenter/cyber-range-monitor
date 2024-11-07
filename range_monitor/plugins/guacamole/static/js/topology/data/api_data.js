/* guac.static/topology/api_data.js */
import { hashDump } from "./hash_data.js";

export { RequestHandler, ConnectionNode, ContextHandler };

class TopologyError extends Error {
  constructor(message) {
    super(
      `TopologyError: something went wrong in the topology.\n[INFO] - ${message}`
    );
    this.name = "TopologyError";
  }
}

class RequestTimeoutError extends Error {
  constructor() {
    super(
      "RequestTimeoutError: the request took too long to complete due to connection or accessibility isssues."
    );
    this.name = "RequestTimeoutError";
  }
}


class RequestHandler {
  static reqErrorMsg(error) {
    return `Request Failed: check your network connection or the may be down. (${error.message})`;
  }
  static jsonErrorMsg(error) {
    return `Failed to parse API response: ${error.message}`;
  }

  /**
   * fetches the guac data from the API
   * endpoint, caller must handle exceptions
   * @param {number} timeoutMs
   * @returns {object[]}
   */
  static async fetchGuacAPI(timeoutMs = 5000) {
    const guacURL = "api/topology_data";
    const controller = new AbortController();
    const { signal } = controller;

    const requestId = setTimeout(() => {
      controller.abort();
    }, timeoutMs);

    const response = await fetch(guacURL, { signal }).catch((error) => {
      clearTimeout(requestId);
      APIHandler.getError(error, APIHandler.reqErrorMsg(error));
    });

    const data = await response.json().catch((error) => {
      clearTimeout(requestId);
      APIHandler.getError(error, APIHandler.jsonErrorMsg(error));
    });

    clearTimeout(requestId);
    this.checkData(data);
    return data.nodes;
  }

  /**
   * @param {Error} errorObj
   * @param {string} errorMsg
   */
  static getError(errorObj, errorMsg) {
    if (errorObj.name === "AbortError") {
      throw new RequestTimeoutError(
        "The request to the Guacamole API timed out, please try again."
      );
    } else {
      throw new TopologyError(errorMsg);
    }
  }

  checkData(data) {
    if (!data) {
      throw new TopologyError("The response from the Guacamole API was empty.");
    }
    if (!data.nodes) {
      throw new TopologyError(
        "The response from the Guacamole API did not return any nodes."
      );
    }
  }
}


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

// const NodeClasses = Object.freeze({
//   [NodeWeight.DEFAULT]: ,
//   [NodeWeight.INACTIVE_ENDPOINT]: ,
//   [NodeWeight.ACTIVE_ENDPOINT]: ,
//   [NodeWeight.GUAC_GROUP]: ,
//   [NodeWeight.ROOT]: ,

// });



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
class ContextUtils {
  static determineWeight(node) {
    if (node.identifier === "ROOT") {
      return NodeWeight.ROOT;
    }
    if (node.type) {
      return NodeWeight.GUAC_GROUP;
    }
    if (node.activeConnections > 0) {
      return NodeWeight.ACTIVE_ENDPOINT;
    }
    if (node.protocol) {
      return NodeWeight.INACTIVE_ENDPOINT;
    }
    return NodeWeight.DEFAULT;
  }
}

/**
 * @class Representation of a node in the topology.
 * @property {string}identifier
 * @property {string} parentIdentifier
 * @property {string} name
 * @property {Object} dump
 * @property {number} weight
 * @property {number} size
 * @property {string} color
 */
class ConnectionNode {
  constructor(jsonData) {
    this.identifier = jsonData.identifier;
    this.parentIdentifier = jsonData.parentIdentifier;
    this.name = jsonData.name;
    this.dump = jsonData;
    // connStyle
    this.weight = ContextUtils.determineWeight(jsonData);
    this.size = this.weight * 3 + 5;
    this.color = colors[this.weight] || colors[NodeWeight.DEFAULT];
    this.type = jsonData.type;
  }
  nodeData() {
    return this.dump;
  }
  isRoot() {
    return this.weight === NodeWeight.ROOT;
  }
  isGroup() {
    return this.weight === NodeWeight.GUAC_GROUP;
  }
  isLeafNode() {
    return (
      this.weight === NodeWeight.ACTIVE_ENDPOINT ||
      this.weight === NodeWeight.INACTIVE_ENDPOINT
    );
  }
  isActive() {
    return this.isGroup() || this.weight === NodeWeight.ACTIVE_ENDPOINT;
  }
}

class ContextHandler {
  /**
   * returns the stateless form of the topology context
   *
   * @param {Object[]} allNodeData
   * @returns {Object{
   *  nodes: ConnectionNode[],
   *  edges: Object[],
   *  nodeMap: Map<string, ConnectionNode>
   * }}
   */
  static getContext(allNodeData) {
    const allNodes = [];
    const edges = [];
    const nodeMap = new Map();

    allNodeData.forEach((node) => {
      if (!node.identifier) {
        return;
      }
      const nodeObj = new ConnectionNode(node);
      allNodes.push(nodeObj);
      nodeMap.set(nodeObj.identifier, nodeObj);
      if (!nodeObj.parentIdentifier) {
        return;
      }
      let parent = allNodeData.find(
        (parentNode) => parentNode.identifier === nodeObj.parentIdentifier
      );
      if (!parent) {
        return;
      }
      edges.push({
        source: parent.identifier,
        target: nodeObj.identifier,
      });
    });
    return {
      nodes: allNodes,
      edges: edges,
      nodeMap: nodeMap,
    };
  }

  /**
   *
   * @param {ConnectionNode[]} allNodes
   * @param {Map<string, ConnectionNode>} nodeMap
   */
  static truncateNodeNames(allNodes, nodeMap) {
    allNodes.forEach((node) => {
      if (!node.isLeafNode()) return;

      let parent = nodeMap.get(node.parentIdentifier);

      if (!parent) return;

      const parentName = parent.name;
      let parentWords = parentName.split(/[^a-zA-Z0-9]+/);

      parentWords.forEach((word) => {
        if (node.name.includes(word)) {
          node.name = node.name.replace(word, "");
        }
      });

      node.name = node.name.replace(/^[^a-zA-Z0-9]+/, "");
    });
  }
}
