// topology/display.js
import { ConnectionData } from "./data/context.js";
import { setupD3, GraphAssets } from "./user-interface/assets.js";
import { RequestHandler } from "./data/request_handler.js";
import { StatusUI } from "./user-interface/ui_hints.js";
import { updateScheduler } from "./refresh.js";
import { settingsModalData } from "./user-interface/node-modal.js/settings-modal.js";
import { Modal } from "./user-interface/node-modal.js/guac-modal.js";

export { Topology };

/**
 *
 * @param {TopologyuserSettings} userSettings
 * @param {Topology} topology
 * @returns {function} - a drag event handler
 */
function setupDrag(scheduler, topology) {
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
		this.userSettings = {
			refreshEnabled: true,
			showInactive: true
		};
		this.scheduler = updateScheduler; 
		this.drag = setupDrag(this.scheduler, this);
		this.assets = new GraphAssets(this.container);
		this.statusUI = new StatusUI();
		this.context = null;
		this.userSelection = [];
	}
	handleRenderError(error, shouldRecreate) {
		if (!shouldRecreate) {
			this.scheduler.pause();
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
			this.handleRenderError(error, shouldRecreate);
		}
	}
	async buildTopology(shouldRecreate) {
		const [data, error] = await RequestHandler.fetchGuacAPI();
		if (error) {
			throw new Error(error);
		}
		// topology has been rendered before
		if(this.context) {
			const filteredData = ConnectionData.filterByStatus(data, this.userSettings.showInactive);
			const hasChanged = this.context.refreshContext(filteredData);
			this.renderTopology(shouldRecreate, hasChanged);
			return;
		} 

		this.context = new ConnectionData();
		this.context.build(data);
		this.renderTopology(true, false);
		
		this.scheduler.setCallback(async () => {
			await this.render();
		});
		console.log("Scheduler started after first render");
		this.scheduler.start();
	}
	createTopology(data) {
		this.context = new ConnectionData();
		this.context.build(data);
		this.renderTopology(true, false);
		
		this.scheduler.setCallback(async () => {
			await this.render();
		});
		console.log("Scheduler started after first render");
		this.scheduler.start();
	}

	updateTopology(data, shouldRecreate) {
		const filteredData = ConnectionData.filterByStatus(data, this.userSettings.showInactive);
		const hasChanged = this.context.refreshContext(filteredData);
		this.renderTopology(shouldRecreate, hasChanged);
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
		if(shouldRecreate) {
			alphaValue = 1;
		} else if(hasChanged) {
			alphaValue = 0.2;
		} else {
			alphaValue = 0;
		}
		console.log(`Alpha Value: ${alphaValue}`);
		
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
	toggleRefresh() {
		this.userSettings.refreshEnabled = !this.userSettings.refreshEnabled;
		if (this.userSettings.refreshEnabled) {
			this.scheduler.start();
		} else {
			this.scheduler.pause();
		}
	}
	async toggleInactive() {
		this.userSettings.showInactive = !this.userSettings.showInactive;
		this.scheduler.pause();
		await this.render();
		if (this.userSettings.refreshEnabled) {
			this.scheduler.start();
		}
	}
}
function initSettingsModal(topology) {
	const { scheduler, context, userSettings } = topology;
	const toggleBtn = ($btn, flag) => {
		const icon = $btn.find("i");
		icon.fadeOut(200, function () {
			if (flag) {
				icon.removeClass("fa-times").addClass("fa-check");
			} else {
				icon.removeClass("fa-check").addClass("fa-times");
			}
			icon.fadeIn(200);
		});
		$btn.toggleClass("active");
	};

	const settingBtnEvents = () => {
		console.log(`refreshEnabled => ${userSettings.refreshEnabled}`);
		$("#toggle-enable-refresh").on("click", function () {
			topology.toggleRefresh();
			toggleBtn($(this), userSettings.refreshEnabled);
			const $speedContainer = $(".refresh-speed");
			if (userSettings.refreshEnabled) {
				$speedContainer.slideDown(300);
			} else {
				$speedContainer.slideUp(300);
			}
		});
		$("#toggle-show-inactive").on("click", function () {
			topology.toggleInactive();
			toggleBtn($(this), userSettings.showInactive);
		});
	};


	const updateRefreshStatus = () => {
		if(userSettings.refreshEnabled) {
			$("#refresh-countdown")
					.text(new Date(scheduler.lastUpdated + scheduler.delay)
					.toLocaleTimeString());			
		} else {
			$("#refresh-countdown").text("Disabled");
		}
	};
	$("#menuToggler").on("click", function () {
		const modalData = settingsModalData(context, scheduler, userSettings);
		const settingsModal = new Modal();
		settingsModal.init("Topology Settings", modalData);
		settingBtnEvents();
		if(!userSettings.refreshEnabled) {
			$(".refresh-speed").hide();
		}
		speedOptionEvents(scheduler, userSettings.refreshEnabled);
		const uptimeId = setUptimeCounter(scheduler.upTime);
		const refreshId = setInterval(() => {
			updateRefreshStatus()
		}, scheduler.delay - 5000);
		settingsModal.openModal(function () {
			clearInterval(uptimeId);
			if(refreshId) {
				clearInterval(refreshId);
			}
		});
	});
}

const speedOptionEvents = (scheduler, refreshEnabled) => {
	$(`.speed-option[data-speed="${scheduler.stringDelay}"]`)
		.addClass("selected");


	$(".speed-option").on("click", function () {	
		if ($(this).hasClass("selected") || !refreshEnabled) {
			return;
		}
		const $current = $(this).attr("data-speed");
		const $speedOptions = $(".speed-option");
		$speedOptions.removeClass("selected");
		$speedOptions
			.find("i.fa-check-square")
			.fadeOut(200, function () {
				$(this)
					.removeClass("fas fa-check-square")
					.addClass("far fa-square")
					.fadeIn(200);
			});
		$(this).addClass("selected");
		$(this)
			.find("i.fa-square")
			.fadeOut(200, function() { 
				$(this)
					.removeClass("far fa-square")
					.addClass("fas fa-check-square")
					.fadeIn(200);
			});			
		const rate = $(this).attr("data-speed");
		const old = scheduler.delay; 
		scheduler.setDelay(rate);
	});
};



function setUptimeCounter(startTime) {
	const uptimeId = setInterval(() => {
		const pad = (num) => {
			return (num < 10)? `0` + num : num;
		};
		
		const elapsed = Math.floor((Date.now() - startTime) / 1000);
		const hours = Math.floor(elapsed / 3600);
		const minutes = Math.floor((elapsed % 3600) / 60);
		const seconds = elapsed % 60;
		$("#uptime-field").text(`${pad(hours)}:${pad(minutes)}:${pad(seconds)}`);	
	}, 1000);
	return uptimeId;
}

