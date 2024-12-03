// topology/data/context.js
import { ConnectionNode } from "./guac-types.js";

/**
 * @class ConnectionData
 * @property {ConnectionNode[]} nodes - The nodes of the connection data.
 * @property {Object[]} edges - The edges of the connection data.
 * @property {Map<string, ConnectionNode>} nodeMap - The map of nodes.
 */
export class ConnectionData {
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
		return apiData.filter(predicate);
	
	}
	/**
	 * clears the context
	 */
	clear() {
		this.nodes = [];
		this.edges = [];
		this.nodeMap = new Map();
	}
	
	/**
	 * builds topology context
	 * @param {Object[]} apiDump 
	 */
	build(apiDump) {
		this.clear();
		const filteredData = ConnectionData.filterByStatus(apiDump, true);
		filteredData.forEach((nodeDump) => {
			this.addNode(nodeDump, filteredData);
		});
		this.shrinkNames(this.nodes);
	}
	/**
	 * @returns {number}
	 */
	countActiveConnections() {
		const activeCount = this.nodes.filter((node) => {
			return node.isLeafNode() && node.isActive();
		}).length;
		return activeCount || 0;
	}
	/**
	 * @param {Object[]} newApiData 
	 * @returns {boolean}
	 */
	refreshContext(newApiData) {
		let hasChanged = false;
		const newDataMap = new Map(newApiData.map((node) => [node.identifier, node]));
		for(let node of this.nodes.slice()) {
			if(!newDataMap.has(node.identifier)) {
				hasChanged = true;
				this.deleteNode(node.identifier);
			}
		}
		for(let nodeDump of newApiData) {
			const existingData = this.nodeMap.get(nodeDump.identifier);
			if(!existingData) {
				hasChanged = true;
				this.addNode(nodeDump, newApiData);
			} else if(!existingData.equals(nodeDump) && !existingData.isRoot()) {
				this.updateNode(nodeDump);
				hasChanged = true;
			}
		}
		return hasChanged;
	}
	updateNode(newData) {
		let oldNode = this.nodeMap.get(newData.identifier);

		if(!oldNode) {
			console.warn("Attempted to update a node that does not exist");
			return;
		}

		const updatedNode = new ConnectionNode(newData);
		this.shrinkName(updatedNode)
		this.nodeMap.set(updatedNode.identifier, updatedNode);

		const index = this.nodes.findIndex((node) => {
			return node.identifier === oldNode.identifier;
		});
		if(index !== -1) {
			this.nodes[index] = updatedNode;
		} else {
			console.warn("attempted to update a node that wasn't in the array???")
		}

		if(updatedNode.isRoot()) {
			return;
		}

		let parent = this.nodeMap.get(updatedNode.parentIdentifier);
		console.log(`parent = ${parent}`);
		this.edges = this.edges.filter((edge) => {
			return !(edge.source === parent.identifier && 
				edge.target === updatedNode.identifier);
		});

		this.edges.push({
			source: parent.identifier,
			target: updatedNode.identifier
		});
	}
	
	addNode(nodeDump, apiDump) {
		if (!nodeDump.identifier) {
			console.warn("Attempted to add a node without an identifier");
			return;
		}
		if (this.nodeMap.has(nodeDump.identifier)) {
			console.warn("Duplicate node identifier detected, was this a mistake?");
			return;
		}

		const newNode = new ConnectionNode(nodeDump, false);
		this.nodeMap.set(newNode.identifier, newNode);
		this.nodes.push(newNode);

		const parent = apiDump.find((parentNode) => {
			return parentNode.identifier === newNode.parentIdentifier
		});
		
		if (!parent) return;

		const edgeExists = this.edges.some((edge) => {
			return edge.source === parent.identifier && 
			edge.target === newNode.identifier
		});

		if (!edgeExists) {
			this.edges.push({
				source: parent.identifier,
				target: newNode.identifier,
			});
		}
	}
	get size() {
		return this.nodes.length;
	}

	filterBy(predicate) {
		return this.nodes.filter(predicate); 
	}



	deleteNode(nodeIdentifier) {
		let oldNode = this.nodeMap.get(nodeIdentifier);
		
		if(!oldNode) return;
		
		let parent = this.nodeMap.get(oldNode.parentIdentifier);
		
		if(parent) {
			this.edges = this.edges.filter((edge) => {
				return !(edge.source === parent.identifier && 
					edge.target === oldNode.identifier);
			});
		}
		
		
		this.nodeMap.delete(nodeIdentifier);
		this.nodes = this.nodes.filter((node) => {
			return node.identifier !== nodeIdentifier;
		});
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











