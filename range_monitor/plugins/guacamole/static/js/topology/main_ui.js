// topology/display.js
import { ConnectionData, ContextHandler } from "./data/context.js";
import { SetupD3, GraphAssets } from "./user-interface/assets.js";
import { RequestHandler } from "./data/request_handler.js";
export { Topology, TopologyController };

/**
 *
 * @param {TopologyController} controller
 * @param {Topology} topology
 * @returns {function} - a drag event handler
 */
function setupDrag(controller, topology) {
	function dragStarted(event, d) {
		if (!event.active) {
			topology.simulation.alphaTarget(0.1).restart();
		}
		d.fx = d.x;
		d.fy = d.y;
		controller.pauseRefresh();
	}
	function dragged(event, d) {
		d.fx = event.x;
		d.fy = event.y;
	}
	function dragEnded(event, d) {
		if (!event.active) {
			topology.simulation.alphaTarget(0.1).restart();
		}
		d.fx = null;
		d.fy = null;

		if (controller.refreshEnabled) {
			controller.scheduleRefresh(() => {
				topology.render();
			}, 5000);
		}
	}
	return d3
		.drag()
		.on("start", dragStarted)
		.on("drag", dragged)
		.on("end", dragEnded);
}

/**
 * @class TopologyController
 * @description
 * responsible for managing the topology state
 * and control flow
 * @property {boolean} refreshEnabled - whether the topology is refreshing
 * @property {boolean} showInactive - whether inactive nodes should be shown
 * @property {Set<string>} userSelection - the selected nodes
 * @property {number|null} updateId - the interval for updating the topology
 */
class TopologyController {
	constructor() {
		this.refreshEnabled = true;
		this.showInactive = true;
		this.userSelection = new Set();
		this.updateId = null;
	}
	/**
	 * clears the updateId property
	 * @param {boolean} shouldDisable - set updateId to null
	 */
	pauseRefresh() {
		if (!this.updateId) return;
		clearInterval(this.updateId);
		this.updateId = null;
	}
	/**
	 * sets the updateId property
	 * for updating the topology
	 * @param {callback} callback
	 * @param {number} ms
	 */
	scheduleRefresh(callback, ms = 5000) {
		this.updateId = setInterval(callback, ms);
	}

	filterNodesByStatus(nodes) {
		let predicate = (node) => {
			return node.identifier && node.activeConnections > 0;
		};

		if (this.showInactive) {
			predicate = (node) => {
				return node.identifier;
			};
		}
		const output = [];
		nodes.forEach((node) => {
			if (predicate(node)) {
				output.push(node);
			}
		});
		return output;
	}
}

function getAlphaValue(isFirstRender, shouldRefresh) {
	if (isFirstRender) return 1;
	else if (shouldRefresh) return 0.1;
	else return 0;
}

/**
 * @class Topology
 * @description Represents the topology of the network, including the SVG elements, simulation, and data handling.
 * @property {Object} svg - The SVG element used for rendering the topology.
 * @property {Object} container - The container element for the SVG.
 * @property {Object} simulation - The D3 simulation object used for force-directed layout.
 * @property {GraphAssets} assets - The assets used for rendering nodes and edges in the topology.
 * @property {TopologyController} controller - The controller responsible for managing topology data and state.
 * @property {GuacContext|null} context - The context containing the current state of nodes and links.
 * @property {Map|null} positions - A map of node positions keyed by node identifier.
 */
class Topology {
	constructor() {
		const { svg, container } = SetupD3.initSVG();
		this.svg = svg;
		this.container = container;
		this.simulation = SetupD3.setupSimulation(svg);
		this.controller = new TopologyController();
		this.drag = setupDrag(this.controller, this);
		this.assets = new GraphAssets(this.container);
	}
	async render(isFirstRender = false) {
		RequestHandler.fetchGuacAPI()
			.then((apiData) => {
				const filteredData = ConnectionData.create(
					apiData,
					this.controller.showInactive
				);
				this.renderTopology(filteredData, isFirstRender);
			})
			.catch((error) => {
				console.error(
					`An error occured while fetching guacamole data: ${error.message}`
				);
			});
	}
	/**
	 *
	 * @param {ConnectionData} parsedNodes
	 * @param {boolean} isFirstRender
	 */
	renderTopology(parsedNodes, isFirstRender) {
		const { nodes, edges, nodeMap } = parsedNodes;
		ContextHandler.truncateNodeNames(nodes, nodeMap);
		this.assets.createLinks(edges, nodeMap);
		// NOTE you MUST set the prevPositions here or Exception, very fun!!
		const prevPositions = new Map(
			this.assets.node
				.data()
				.map((d) => [`${d.identifier}`, { x: d.x, y: d.y }])
		);

		const nodeContext = {
			userSelection: this.controller.userSelection,
			nodes: nodes,
			nodeMap: nodeMap,
		};

		this.assets.setNodes(this.drag, nodeContext);
		this.assets.setLabels(nodes);
		this.simulation.nodes(nodes);

		let shouldRefresh = false;
		nodes.forEach((node) => {
			const prev = prevPositions.get(node.identifier);
			if (prev) {
				Object.assign(node, prev);
			} else {
				shouldRefresh = true;
			}
		});

		const alphaValue = getAlphaValue(isFirstRender, shouldRefresh);

		this.simulation.force("link").links(edges);
		this.simulation.alpha(alphaValue).restart();

		this.simulation.on("tick", () => {
			this.assets.onTick();
		});
	}
	toggleRefresh() {
		this.controller.refreshEnabled = !this.controller.refreshEnabled;
		if (this.controller.refreshEnabled) {
			this.controller.scheduleRefresh(() => {
				this.render();
			});
		} else {
			this.controller.pauseRefresh();
		}
	}
	toggleInactive() {
		this.controller.showInactive = !this.controller.showInactive;
		this.render()
			.then(() => {
				this.controller.pauseRefresh();
				if (this.controller.refreshEnabled) {
					this.controller.scheduleRefresh(() => {
						this.render();
					});
				}
			})
			.catch((error) => {
				console.error(
					`An error occured while toggling ionactive nodes: ${error.message}`
				);
			});
	}
}
