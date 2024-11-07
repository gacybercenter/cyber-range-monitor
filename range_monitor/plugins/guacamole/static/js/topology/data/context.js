// topology/data/context.js
import { ConnectionNode } from "./guac_types.js";
/* 
  NOTE: remove context handler export once ConnectionData is imp'd
*/


export { ConnectionData, ContextHandler };


class ConnectionData {
  /**
   * @property {ConnectionNode[]} nodes - the nodes of the topology
   * @property {Object[{source: {string}, target{string}}]} edges - the edges of the topology
   */
  constructor(apiData) {
    this.clear();
    this.initialize(apiData);
  }
  static create(apiData, filterBy) {
    if(!apiData) {
      throw new Error("No data was provided to create ConnectionData");
    }
    const filteredData = ConnectionData.filterByStatus(apiData, filterBy);
    return new ConnectionData(filteredData, filterBy);
  }
  /**
   * 
   * @param {object[]} apiData 
   * @param {boolean} showInactive 
   * @returns {object[]}
   */
  static filterByStatus(apiData, showInactive) {
    let predicate = (node) => {
			return node.identifier && node.activeConnections > 0;
		};

		if (showInactive) {
			predicate = (node) => node.identifier;
		}

		const output = [];
		nodes.forEach((node) => {
			if (predicate(node)) {
				output.push(node);
			}
		});
		
    return output;
  }
  /**
   * clears the context 
   */
  clear() {
    this.nodes = [];
    this.edges = [];
    this.nodeMap = new Map();
  }

  initialize(apiData) {
    const { nodes, edges, nodeMap } = ContextHandler.getContext(apiData);
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
   * @param {Object[]} apiData
   * @returns {Object{
   *  nodes: ConnectionNode[],
   *  edges: Object[],
   *  nodeMap: Map<string, ConnectionNode>
   * }}
   */
  static getContext(apiData) {
    const allNodes = [];
    const edges = [];
    const nodeMap = new Map();

    apiData.forEach((node) => {
      if (!node.identifier) {
        return;
      }
      const nodeObj = new ConnectionNode(node);
      allNodes.push(nodeObj);
      nodeMap.set(nodeObj.identifier, nodeObj);
      if (!nodeObj.parentIdentifier) {
        return;
      }
      let parent = apiData.find(
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