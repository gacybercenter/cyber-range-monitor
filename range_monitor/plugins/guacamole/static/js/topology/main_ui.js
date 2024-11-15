// topology/display.js
import { ConnectionData } from "./data/context.js";
import { setupD3, GraphAssets } from "./user-interface/assets.js";
import { RequestHandler } from "./data/request_handler.js";
import { StatusUI } from "./user-interface/ui_hints.js";
import { updateScheduler } from "./refresh.js";
import { initSettingsModal, UserSettings } from "./user-settings.js";

export { Topology };

/**
 *
 * @param {TopologyuserSettings} userSettings
 * @param {Topology} topology
 * @returns {function} - a drag event handler
 */
function setupDrag(updateScheduler, topology) {
	function dragStarted(event, d) {
		if (!event.active) {
			topology.simulation.alphaTarget(0.1).restart();
		} 
		d.fx = d.x;
		d.fy = d.y;
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
	}
	return d3
		.drag()
		.on("start", dragStarted)
		.on("drag", dragged)
		.on("end", dragEnded);
}


/* 
	TODO

	-Move assets into seperate class that 
	handles rendering the nodes & managing 
	simulation passed data by the Context

	-Implement UserSettings 

	-Reimplement fetch routine 
*/


/**
 * @class Topology
 * @description Represents the topology of the network, including the SVG elements, simulation, and data handling.
 * @property {Object} svg - The SVG element used for rendering the topology.
 * @property {Object} container - The container element for the SVG.
 * @property {Object} simulation - The D3 simulation object used for force-directed layout.
 * @property {GraphAssets} assets - The assets used for rendering nodes and edges in the topology.
 * @property {TopologyuserSettings} userSettings - The userSettings responsible for managing topology data and state.
 * @property {StatusUI} statusUI - A map of node positions keyed by node identifier.
 */
class Topology {
	constructor() {
		const { svg, container } = setupD3.initSVG();
		this.svg = svg;
		this.container = container;
		setupD3.setupFilters(container);
		this.simulation = setupD3.setupSimulation(svg);
		this.userSettings = new UserSettings();
		this.updateScheduler = updateScheduler; 
		this.drag = setupDrag(this.updateScheduler, this);
		this.assets = new GraphAssets(this.container);
		this.statusUI = new StatusUI();
		this.context = null;
		this.userSelection = [];
	}
	handleRenderError(error, shouldRecreate) {
		if (!shouldRecreate) {
			this.updateScheduler.pause();
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
	 * @param {bool} shouldRecreate
	 * @returns {Promise<void>}
	 */
	async render(shouldRecreate = false) {
		try {
			await this.buildTopology(shouldRecreate);
		} catch (error) {
			console.log(`[RENDER_ERROR] -> ${error.message}`);
			this.handleRenderError(error, shouldRecreate);
		}
	}
	async buildTopology(shouldRecreate) {
		// ignore IDE warning, you need to await this 
		const [apiData, error] = await RequestHandler.fetchGuacAPI();
		if (error) {
			throw new Error(error);
		}

		if(this.context) {
			this.updateTopology(apiData, shouldRecreate)
		} else {
			this.createTopology(apiData, shouldRecreate);
		}
		
		const { refreshEnabled } = this.userSettings;
		const { isRunning } = this.updateScheduler;

		if(refreshEnabled && !isRunning) {
			this.updateScheduler.start();
		} else if(!refreshEnabled && updateScheduler.isRunning) {
			this.updateScheduler.pause();
		}
	}

	createTopology(data, shouldRecreate) {
		this.context = new ConnectionData();
		this.context.build(data);
		this.renderTopology(shouldRecreate, false);
		
		if(this.updateScheduler.isRunning) {
			return;
		}
		this.updateScheduler.setCallback(async () => {
			await this.render();
		});
		this.updateScheduler.start();
	}

	updateTopology(data, shouldRecreate) {
		const filteredData = ConnectionData.filterByStatus(data, this.userSettings.showInactive);
		const hasChanged = this.context.refreshContext(filteredData);
		if(hasChanged) {
			this.renderTopology(shouldRecreate, hasChanged);
		}
	}

	addSimulationTick() {
		this.simulation.on("tick", () => {
			this.assets.onTick();
		});
	}

	/**
	 *
	 * @param {ConnectionData} connectionContext
	 * @param {boolean} shouldRecreate
	 */
	renderTopology(shouldRecreate, hasChanged) {
		const { nodes, edges, nodeMap } = this.context;
		/* 
			for some reason d3 mutates the edges array and wasted 2 hours of my life 
			try it yourself and watch as time evaporates 
		*/
		const clonedEdges = edges.map((edge) => ({ ...edge }));	
		this.assets.createLinks(clonedEdges, nodeMap);

		const nodeData = {
			userSelection: this.userSelection,
			nodes: nodes,
			nodeMap: nodeMap,
		};

		this.assets.setNodes(this.drag, nodeData);
		
		this.assets.setLabels(nodes);
		this.assets.setIcons(nodes);
		this.simulation.nodes(nodes);

		let alphaValue;
		console.log(`Should Recreate: ${shouldRecreate}, Has Changed: ${hasChanged}`);
		if(shouldRecreate) {
			alphaValue = 1;
		} else if(hasChanged) {
			alphaValue = 0.1;
		} else {
			alphaValue = 0;
		}
		console.log(`Resulting Alpha Value: ${alphaValue}`);
		
		this.simulation
			.force("link")
			.links(clonedEdges);

		this.simulation
			.alpha(alphaValue)
			.alphaTarget(0.1)
			.restart();
	
		if (shouldRecreate) {
			this.addSimulationTick();
			this.statusUI.hide();
			initSettingsModal(this);
		}
	}
	async toggleRefresh() {
		this.userSettings.refreshEnabled = !this.userSettings.refreshEnabled;
		if (this.userSettings.refreshEnabled) {
			await this.render();
		} else {
			this.updateScheduler.pause();
		}
	}
	async toggleInactive() {
		this.userSettings.showInactive = !this.userSettings.showInactive;
		this.updateScheduler.pause();
		await this.render();
	}
}


