// topology/data/guac_types.js
import hash from "./hash_data.js";
export { ConnectionNode, NodeWeight, NodeColors };



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
 * @enum {string} NodeClasses
 * the css class for the nodes 
 */
const NodeClasses = Object.freeze({
  [NodeWeight.DEFAULT]: "default-conn" ,
  [NodeWeight.INACTIVE_ENDPOINT]: "inactive-conn",
  [NodeWeight.ACTIVE_ENDPOINT]: "active-conn",
  [NodeWeight.GUAC_GROUP]: "conn-group",
  [NodeWeight.ROOT]: "root",
});

/**
 * @enum {string} NodeColors
 * @description  the NodeColors associated with each node weight.
 */
const NodeColors = Object.freeze({
	[NodeWeight.DEFAULT]: "rgb(0, 0, 0)", // black
	[NodeWeight.INACTIVE_ENDPOINT]: "rgb(192, 0, 0)", // red
	[NodeWeight.ACTIVE_ENDPOINT]: "rgb(0, 192, 0)", // green
	[NodeWeight.GUAC_GROUP]: "rgb(0, 0, 192)", // blue
	[NodeWeight.ROOT]: "rgb(255, 255, 255)", // white
});

/**
 * @enum {string} fasIconUnicode
 * due to the limitations of d3 
 * we have to use the unicode values 
 * of the font awesome icons in the topology circles
 */
const fasIconUnicode = Object.freeze({
	SERVER: "\uf233", // fa-solid fa-server
	COMPUTER: "\uf109", // fa-solid fa-laptop
	WINDOWS: "\uf17a", // fa-brands fa-windows
	LINUX: "\uf17c", // fa-brands fa-linux
	NETWORK: "\uf6ff", // fa-solid fa-network-wired
	DEFAULT: "\uf128", // fa-solid fa-question
});

/**
 * @enum {string} TopologyIcons
 * the unicode values of the font awesome icons
 * associated with each node weight
 */
const TopologyIcons = Object.freeze({
	[NodeWeight.ACTIVE_ENDPOINT]: fasIconUnicode.COMPUTER,
	[NodeWeight.INACTIVE_ENDPOINT]: fasIconUnicode.COMPUTER,
	[NodeWeight.ROOT]: fasIconUnicode.SERVER,
	[NodeWeight.GUAC_GROUP]: fasIconUnicode.NETWORK,
	[NodeWeight.DEFAULT]: fasIconUnicode.DEFAULT,
});


/**
 * @class Representation of all connections / node in the topology.
 * @property {string}identifier
 * @property {string} parentIdentifier
 * @property {string} name
 * @property {Object} dump
 * @property {number} weight
 * @property {number} size
 * @property {string} color
 */
class ConnectionNode {
	/**
	 * @param {object} jsonData 
	 */
	constructor(jsonData) {
		this.identifier = jsonData.identifier;
		this.parentIdentifier = jsonData.parentIdentifier;
		this.name = jsonData.name;
		this.dump = jsonData;
		this.hashed = hash(this.dump);
		// connStyle
		this.weight = getNodeWeight(jsonData);
		this.size = this.weight * 5 + 5;
		this.color = NodeColors[this.weight] || NodeColors[NodeWeight.DEFAULT];
		this.type = jsonData.type;
		
		this.icon = TopologyIcons[this.weight] || TopologyIcons[NodeWeight.DEFAULT];
		this.cssClass = NodeClasses[this.weight] || NodeClasses[NodeWeight.DEFAULT];
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
	getOsIcon() {
		let fasClass; 
		if(this.isGroup()) {
	    fasClass = "fa-solid fa-network-wired"			
		}
		else if(this.name.toLowerCase().includes("win")) {
			fasClass = "fa-brands fa-windows";
		} else {
			fasClass = "fa-brands fa-linux";
		}
		return `<i class="os-icon ${fasClass}"></i>`;
	}

	/**
	 * NOTE: this uses the other API object (not connection node instance)
	 * and compares it to the Connection Nodes Instances API Object
	 * (this.dump) to determine if the node has changed.
	 * @param {Object} nodeDump 
	 * @returns {Boolean}
	 */
	equals(nodeDump) {
		return this.hashed === hash(nodeDump);
	}
}

/**
 * @param {ConnectionNode} node
 * @returns {number|NodeWeight}
 */
function getNodeWeight(node) {
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
