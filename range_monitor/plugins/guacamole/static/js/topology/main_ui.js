// topology/display.js
import { ConnectionData } from "./data/context.js";
import { SetupD3, GraphAssets } from "./user-interface/assets.js";
import { RequestHandler } from "./data/request_handler.js";
import { StatusUI } from "./user-interface/ui_hints.js";
export { Topology };

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
		controller.pauseUpdates();
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
			controller.scheduleUpdates(async () => {
				await topology.render();
			}, 5000);
		}
	}
	return d3
		.drag()
		.on("start", dragStarted)
		.on("drag", dragged)
		.on("end", dragEnded);
}


const topologyControls = {
	refreshEnabled: true,
	showInactive: true,
	updateId: null,
	lastUpdated: null,
	pauseUpdates() {
		if (!this.updateId) {
			return;
		}
		clearInterval(this.updateId);
		this.updateId = null;
	},
	scheduleUpdates(callback, ms = 5000) {
		if (this.updateId) {
			return;
		}
		self.updateId = setInterval(callback, ms);
	},
	setupSettings(topology) {
		if (this.settingsEnabled) {
			return;
		}

		const toggleBtnAppearance = ($btn) => {
			$btn.toggleClass("on off").find(".opt-icon")
					.toggleClass("fa-check fa-times");
		};

		$("#refreshBtn").on("click", function () {
			topology.toggleRefresh();
			toggleBtnAppearance($(this));
		});

		$("#inactiveBtn").on("click", function () {
			topology.toggleInactive();
			toggleBtnAppearance($(this));
		});

		$("#menuToggler").on("click", function () {
			$("#settingsMenu").toggleClass("active inactive");
		});
	}
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


function getAlphaValue(isFirstRender, shouldRefresh) {
	if (isFirstRender) {
		return 1;
	}
	else if (shouldRefresh) {
		return 0.1;
	}
	else {
		return 0;
	}
}

/**
 * @class Topology
 * @description Represents the topology of the network, including the SVG elements, simulation, and data handling.
 * @property {Object} svg - The SVG element used for rendering the topology.
 * @property {Object} container - The container element for the SVG.
 * @property {Object} simulation - The D3 simulation object used for force-directed layout.
 * @property {GraphAssets} assets - The assets used for rendering nodes and edges in the topology.
 * @property {TopologyController} controller - The controller responsible for managing topology data and state.
 * @property {StatusUI} statusUI - A map of node positions keyed by node identifier.
 */
class Topology {
	constructor() {
		const { svg, container } = SetupD3.initSVG();
		this.svg = svg;
		this.container = container;
		SetupD3.setupFilters(container);
		this.simulation = SetupD3.setupSimulation(svg);
		this.controller = topologyControls;
		this.drag = setupDrag(this.controller, this);
		this.assets = new GraphAssets(this.container);
		this.statusUI = new StatusUI();
		this.context = null;
		this.userSelection = [];
	}
		handleRenderError(error, isFirstRender) {
			if (!isFirstRender) {
				this.controller.pauseUpdates();
				alert(`The topology failed to refresh and will not be updated: ${error.message}`);
				return;
			}

			const $retryBtn = this.statusUI.toErrorMessage(error.message);
			$retryBtn.on("click", async () => {
				this.statusUI.toLoading();
				await this.render(true);
			});
	}



	/**
	 * @param {bool} isFirstRender
	 * @returns {Promise<void>}
	 */
	async render(isFirstRender = false) {
		try {
			await this.buildTopology(isFirstRender);
		} catch (error) {
			this.handleRenderError(error, isFirstRender);
		}
	}
	async buildTopology(isFirstRender) {
		const [data, error] = await RequestHandler.fetchGuacAPI();
		if (error) {
			throw new Error(error);
		}
		const context = new ConnectionData(data);
		context.build(data);
		this.context = context;
		this.renderTopology(context, isFirstRender);
	}

	/**
	 *
	 * @param {ConnectionData} connectionContext
	 * @param {boolean} isFirstRender
	 */
	renderTopology(connectionContext, isFirstRender) {
		const { nodes, edges, nodeMap } = connectionContext;
		this.assets.createLinks(edges, nodeMap);
		
		// NOTE you MUST set the prevPositions here or Exception, very fun!!
		const prevPositions = new Map(
			this.assets.node
				.data()
				.map((d) => [`${d.identifier}`, { x: d.x, y: d.y }])
		);

		const nodeContext = {
			userSelection: this.userSelection,
			nodes: nodes,
			nodeMap: nodeMap,
		};

		this.assets.setNodes(this.drag, nodeContext);
		this.assets.setLabels(nodes);
		this.assets.setIcons(nodes);
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
		this.simulation.alpha(alphaValue).alphaTarget(0).restart();
		this.simulation.on("tick", () => {
			this.assets.onTick();
			if(this.simulation.alpha() < 0.01) {
				this.simulation.stop();
			}
		});

		if (isFirstRender) {
			this.statusUI.hide();
			this.controller.setupSettings(this);
		}
	}
	toggleRefresh() {
		this.controller.refreshEnabled = !this.controller.refreshEnabled;
		if (this.controller.refreshEnabled) {
			this.controller.scheduleUpdates(async () => {
				await this.render();
			});
		} else {
			this.controller.pauseUpdates();
		}
	}
	async toggleInactive() {
		this.controller.showInactive = !this.controller.showInactive;
		await this.render();
		this.controller.pauseUpdates();
		if (this.controller.refreshEnabled) {
			this.controller.scheduleUpdates(async () => {
				await this.render();
			});
		}
	}
}
