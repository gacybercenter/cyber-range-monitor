// topology/display.js
import { ConnectionData } from "./data/context.js";
import { setupD3, GraphAssets } from "./user-interface/assets.js";
import { RequestHandler } from "./data/request_handler.js";
import { LoadScreen } from "./user-interface/ui_hints.js";
import { updateScheduler } from "./refresh.js";
import { initSettingsModal, UserSettings } from "./user-settings.js";



/* 
	TODO

	-Move assets into seperate class that 
	handles rendering the nodes & managing 
	simulation passed data by the Context

	-Implement UserSettings 

	-Reimplement fetch routine 
*/



class GraphUI {
	constructor() {
		const { svg, container } = setupD3.initSVG();
		this.svg = svg;
		this.container = container;
		setupD3.setupFilters(container);
		this.simulation = setupD3.setupSimulation(svg);
		this.drag = this.setupDrag();
		this.assets = new GraphAssets(this.container);
		this.tickAdded = false;
	}
	/**
	 * @returns {function} - a drag event handler
	 */
	setupDrag() {
		const dragStarted = (event, d) => {
			if (!event.active) {
				this.simulation.alphaTarget(0.1).restart();
			} 
			d.fx = d.x;
			d.fy = d.y;
		};

		const dragged = (event, d) => {
			d.fx = event.x;
			d.fy = event.y;
		};

		const dragEnded = (event, d) => {
			if (!event.active) {
				this.simulation.alphaTarget(0.1).restart();
			}
			d.fx = null;
			d.fy = null;
		};

		return d3
			.drag()
			.on("start", dragStarted)
			.on("drag", dragged)
			.on("end", dragEnded);
	}
	/**
	 * @param {ConnectionData} context 
	 * @param {String[]} userSelection 
	 */
	setAssetData(context, clonedEdges, userSelection) {
		this.assets.setEdges(clonedEdges, context.nodeMap);
		this.assets.setNodes(this.drag, userSelection, context);
		this.assets.setLabels(context.nodes);
		this.assets.setIcons(context.nodes);
		this.simulation.nodes(context.nodes);
		this.simulation.force("link").links(clonedEdges);
	}
	restartSimulation(alphaValue) {
		this.simulation
			.alpha(alphaValue)
			.alphaTarget(0.1)
			.restart();

		if(this.tickAdded) {
			return;
		}
		console.log("Adding Tick Event Listener");
		this.simulation.on("tick", () => {
			this.assets.onTick();
		});
		this.tickAdded = true;
	}
}

export class Topology {
	constructor() {
		this.display = new GraphUI();
		this.userSettings = new UserSettings();
		this.statusUI = new LoadScreen();
		this.updateScheduler = updateScheduler; 
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
		if(error) {
			throw new Error(error);
		}
		
		if(this.context) {
			this.updateTopology(apiData, shouldRecreate);
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

	createTopology(apiData, shouldRecreate) {
		this.context = new ConnectionData();
		this.context.build(apiData);
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
		const filteredData = ConnectionData.filterByStatus(
			data, this.userSettings.showInactive
		);

		const hasChanged = this.context.refreshContext(filteredData);
		if(hasChanged) {
			this.renderTopology(shouldRecreate, hasChanged);
		}
	}
	
	renderTopology(shouldRecreate, hasChanged) {
		/* NOTE 
			for some reason d3 mutates the edges array and 
			wasted 2 hours of my life try it yourself and 
			watch as time evaporates 
		*/
		const clonedEdges = this.context.edges.map((edge) => ({ ...edge }));	
		this.display.setAssetData(this.context, clonedEdges, this.userSelection)
		
		console.log(`Should Recreate: ${shouldRecreate}, Has Changed: ${hasChanged}`);	
		let alphaValue;
		if(shouldRecreate) {
			alphaValue = 1;
		} else if(hasChanged) {
			alphaValue = 0.1;
		} else {
			alphaValue = 0;
		}
		console.log(`Resulting Alpha Value: ${alphaValue}`);
		this.display.restartSimulation(alphaValue);
		
		if(shouldRecreate) {
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