// topology/data/context.js
import { ConnectionNode } from "./connectionNode.js";
/* 
  NOTE: remove context handler export once ConnectionData is imp'd
*/


export { ConnectionData, ContextHandler };


class ConnectionData {
  /**
   * @property {ConnectionNode[]} nodes - the nodes of the topology
   * @property {Object[{source: {string}, target{string}}]} edges - the edges of the topology
   */
  constructor() {
    this.clear();
    this.initialize(allNodeData);
  }

  clear() {
    this.nodes = [];
    this.edges = [];
    this.nodeMap = new Map();
  }

  initialize(allNodeData) {
    const { nodes, edges, nodeMap } = ContextHandler.getContext(allNodeData);
    this.nodes = nodes;
    this.edges = edges;
    this.nodeMap = nodeMap;
  }
  getChildNodes(groupIdentifier) {
    const groupNode = this.nodeMap.get(groupIdentifier);
    if(!groupNode) {
      console.log("Group identifier not found in nodeMap");
      return [];
    }
    if(!groupNode.isGroup()) {
      console.log("Connection is not a group node");
      return [];
    }
    const children = this.nodes.filter(node => node.parentIdentifier === groupIdentifier);
    return children || [];
  }
  countActiveConnections() {
    const active = this.nodes.filter((node) => {
      return node.isLeafNode() && node.isActive();
    });
    return active ? active.length : 0;
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
      
      if (!parent) return;
      
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