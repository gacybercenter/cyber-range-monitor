/* guac.static/topology/api_data.js */
import { hashDump } from "./hash_data.js";

export { ContextHandler };
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


class ContextUtils {
  static determineWeight(node) {
    if(node.identifier === "ROOT") {
      return NodeWeight.ROOT;
    }
    if(node.type) {
      return NodeWeight.GUAC_GROUP;
    }
    if(node.activeConnections > 0) {
      return NodeWeight.ACTIVE_ENDPOINT;
    }
    if(node.protocol) {
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
      if(!parent) {
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
    // const endpoints = this.getEndpoints();
    //     endpoints.forEach((endpoint) => {
    //       let parent = this.groups.find(
    //         (group) => group.identifier === endpoint.parentIdentifierentifier
    //       );
    //       let parentName = parent.name;
    //       let
    //       parentWords.forEach((word) => {
    //         if (endpoint.name.includes(word)) {
    //           endpoint.name = endpoint.name.replace(word, "");
    //         }
    //       });
    //       endpoint
    //     });
  }
}
