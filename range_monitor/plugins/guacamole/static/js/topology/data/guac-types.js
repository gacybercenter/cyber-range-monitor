// topology/data/guac-types.js
import hash from "./hash-data.js";
export { ConnectionNode, NODE_WEIGHT, NODE_COLORS };



/**
 * @enum {number} NODE_WEIGHT
 * @description Defines the weight categories for nodes.
 */
const NODE_WEIGHT = Object.freeze({
	ROOT: 5,
	GUAC_GROUP: 4,
	ACTIVE_ENDPOINT: 3,
	INACTIVE_ENDPOINT: 2,
	DEFAULT: 1,
});

/**
 * @enum {string} NODE_CLASSES
 * the css class for the nodes 
 */
const NODE_CLASSES = Object.freeze({
  [NODE_WEIGHT.DEFAULT]: "default-conn" ,
  [NODE_WEIGHT.INACTIVE_ENDPOINT]: "inactive-conn",
  [NODE_WEIGHT.ACTIVE_ENDPOINT]: "active-conn",
  [NODE_WEIGHT.GUAC_GROUP]: "conn-group",
  [NODE_WEIGHT.ROOT]: "root",
});

/**
 * @enum {string} NODE_COLORS
 * @description  the NODE_COLORS associated with each node weight.
 */
const NODE_COLORS = Object.freeze({
	[NODE_WEIGHT.DEFAULT]: "rgb(0, 0, 0)", // black
	[NODE_WEIGHT.INACTIVE_ENDPOINT]: "rgb(192, 0, 0)", // red
	[NODE_WEIGHT.ACTIVE_ENDPOINT]: "rgb(0, 192, 0)", // green
	[NODE_WEIGHT.GUAC_GROUP]: "rgb(0, 0, 192)", // blue
	[NODE_WEIGHT.ROOT]: "rgb(255, 255, 255)", // white
});

/**
 * @enum {string} ICON_UNICODE
 * due to the limitations of d3 
 * we have to use the unicode values 
 * of the font awesome icons in the topology circles
 */
const ICON_UNICODE = Object.freeze({
	SERVER: "\uf233", // fa-solid fa-server
	COMPUTER: "\uf109", // fa-solid fa-laptop
	WINDOWS: "\uf17a", // fa-brands fa-windows
	LINUX: "\uf17c", // fa-brands fa-linux
	NETWORK: "\uf6ff", // fa-solid fa-network-wired
	DEFAULT: "\uf128", // fa-solid fa-question
});

/**
 * @enum {string} NODE_ICONS
 * the unicode values of the font awesome icons
 */
const NODE_ICONS = Object.freeze({
	[NODE_WEIGHT.ACTIVE_ENDPOINT]: ICON_UNICODE.COMPUTER,
	[NODE_WEIGHT.INACTIVE_ENDPOINT]: ICON_UNICODE.COMPUTER,
	[NODE_WEIGHT.ROOT]: ICON_UNICODE.SERVER,
	[NODE_WEIGHT.GUAC_GROUP]: ICON_UNICODE.NETWORK,
	[NODE_WEIGHT.DEFAULT]: ICON_UNICODE.DEFAULT,
});

/**
 * @enum {string} OS_FAS_ICONS 
 * the fas icon class for os 
 */
const OS_FAS_ICONS = Object.freeze({
	WINDOWS: "fa-brands fa-windows",
	LINUX: "fa-brands fa-linux",
	SERVER: "fa-solid fa-server",
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
	 * @param {object} jsonData - the dump of the connection node returned by the API
	 */
	constructor(jsonData) {
		this.identifier = jsonData.identifier;
		this.parentIdentifier = jsonData.parentIdentifier;
		this.name = jsonData.name;
		this.dump = jsonData;
		this.hashed = hash(this.dump);
		// connStyle
		this.weight = getNodeWeight(jsonData);
		this.size = (this.weight * 5) + 5;
		this.color = NODE_COLORS[this.weight] || NODE_COLORS[NODE_WEIGHT.DEFAULT];
		this.type = jsonData.type;
		
		this.icon = NODE_ICONS[this.weight] || NODE_ICONS[NODE_WEIGHT.DEFAULT];
		this.cssClass = NODE_CLASSES[this.weight] || NODE_CLASSES[NODE_WEIGHT.DEFAULT];
	}

	isRoot() {
		return this.weight === NODE_WEIGHT.ROOT;
	}
	
	isGroup() {
		return this.weight === NODE_WEIGHT.GUAC_GROUP;
	}

	isLeafNode() {
		return (
			this.weight === NODE_WEIGHT.ACTIVE_ENDPOINT ||
			this.weight === NODE_WEIGHT.INACTIVE_ENDPOINT
		);
	}
	isActive() {
		return this.isGroup() || this.weight === NODE_WEIGHT.ACTIVE_ENDPOINT;
	}
	getOsIcon() {
		let fasClass; 
		const { protocol } = this.dump;
		if(this.isGroup() || !protocol) {
	    fasClass = OS_FAS_ICONS.SERVER;			
		} else if(protocol.toLowerCase() === "rdp") {
			fasClass = OS_FAS_ICONS.WINDOWS;
		} else {
			fasClass = OS_FAS_ICONS.LINUX;
		}
		return `<i class="os-icon ${fasClass}"></i>`;
	}
	get activeConnections() {
		return this.dump.activeConnections || 0;
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
 * @returns {number|NODE_WEIGHT}
 */
function getNodeWeight(node) {
	if (node.identifier === "ROOT") {
		return NODE_WEIGHT.ROOT;
	}
	if (node.type) {
		return NODE_WEIGHT.GUAC_GROUP;
	}
	if (node.activeConnections > 0) {
		return NODE_WEIGHT.ACTIVE_ENDPOINT;
	}
	if (node.protocol) {
		return NODE_WEIGHT.INACTIVE_ENDPOINT;
	}
	return NODE_WEIGHT.DEFAULT;
}
