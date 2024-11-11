// topology/data/context.js
import { ConnectionNode } from "./guac_types.js";
/* 
  NOTE: remove context handler export once ConnectionData is imp'd
*/

export { ConnectionData };



class ConnectionData {
	/**
	 * @property {ConnectionNode[]} nodes - the nodes of the topology
	 * @property {Object[{source: {string}, target{string}}]} edges - the edges of the topology
	 */
	constructor() {
		this.clear();
	}
	/**
	 * @param {object[]} apiData
	 * @param {CallableFunction} filterBy
	 * @returns {ConnectionData}
	 */
	static create(apiData, filterBy) {
		if (!apiData) {
			throw new Error("No data was provided to create ConnectionData");
		}
		const filteredData = ConnectionData.filterByStatus(apiData, filterBy);
		return new ConnectionData(filteredData);
	}

	/**
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
		const output = apiData.filter(predicate);
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
	getChildNodes(groupIdentifier) {
		const groupNode = this.nodeMap.get(groupIdentifier);
		
		if (!groupNode) {
			console.log("Group identifier not found in nodeMap");
			return [];
		}

		if (!groupNode.isGroup()) {
			console.log("Connection is not a group node");
			return [];
		}

		const children = this.nodes.filter((node) => {
			return node.parentIdentifier === groupIdentifier;
		});

		return children || [];
	}
	/**
	 * @returns {number}
	 */
	countActiveConnections() {
		const active = this.nodes.filter((node) => {
			return node.isLeafNode() && node.isActive();
		});
		return active ? active.length : 0;
	}
	/**
	 * @param {Object[]} newApiData 
	 * @returns {boolean}
	 */
	hasChanged(newApiData) {
		let hasChanged = false;
		newApiData.forEach((nodeDump) => {
			let existingData = this.nodeMap.get(nodeDump.identifier);
			if(!existingData) {
				hasChanged = true;
				this.addNode(nodeDump, newApiData);
				return;
			}
			if(!existingData.equals(nodeDump)) {
				console.log(`Node ${nodeDump.identifier} has been updated`);
				hasChanged = true;
				this.updateNode(nodeDump);
			}
		});
		return hasChanged;
	}

	getRoot() {
		return this.nodeMap.get("ROOT");
	}

	updateNode(newData) {
		let oldNode = this.nodeMap.get(newData.identifier);
		if(!oldNode) {
			return;
		}
		const updated = new ConnectionNode(newData, true);
		this.nodeMap.set(updated.identifier, updated);
		let oldData = this.nodes.find((node) => {
			return node.identifier !== updated.identifier;
		});
		if(oldData) {
			Object.assign(oldData, updated);
		}
	}
	addNode(nodeDump, apiDump) {
		if(!nodeDump.identifier) {
			return;
		}
		const newNode = new ConnectionNode(nodeDump);
		this.nodeMap.set(newNode.identifier, newNode);
		this.nodes.push(newNode);
		let parent = apiDump.find((parentNode) => {
			return parentNode.identifier === newNode.parentIdentifier
		});
		if(parent) {
			this.edges.push({
				source: parent.identifier,
				target: newNode.identifier,
			});
		}
	}

	deleteNode(nodeIdentifier) {
		let oldNode = this.nodeMap.get(nodeIdentifier);
		if(!oldNode) {
			return;
		}
		let parent = this.nodeMap.get(oldNode.parentIdentifier);
		if(parent) {
			this.edges = this.edges.filter((edge) => {
				return edge.source !== parent.identifier && 
				edge.target !== oldNode.identifier;
			});
		}
		this.nodeMap.delete(nodeIdentifier);
		this.nodes = this.nodes.filter((node) => {
			return node.identifier !== nodeIdentifier;
		});
	}



	build(apiData) {
		this.clear();
		apiData.forEach((node) => {
			this.addNode(node, apiData);
		});
		this.shrinkNames(this.nodes);
	}
	shrinkName(node) {
		if (!node.isLeafNode()) return;
		let parent = this.nodeMap.get(node.parentIdentifier);

		if (!parent) return;

		const parentName = parent.name;
		let parentWords = parentName.split(/[^a-zA-Z0-9]+/);

		parentWords.forEach((word) => {
			if (node.name.includes(word)) {
				node.name = node.name.replace(word, "");
			}
		});
		node.name = node.name.replace(/^[^a-zA-Z0-9]+/, "");
	}
	shrinkNames(nodeSelection) {
		nodeSelection.forEach((node) => {
			this.shrinkName(node);
		});
	}

}











