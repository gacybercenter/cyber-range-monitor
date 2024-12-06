// topology/render.js
import { ConnectionData } from "./data/context.js";
import { GraphUI } from "./user-interface/assets.js";
import { LoadScreen } from "./user-interface/misc/ui_hints.js";
import { updateScheduler } from "./refresh.js";
import { settingsUI, UserSettings } from "./settings/user-settings.js";


export const topology = {
	display: new GraphUI(),
	userSettings: new UserSettings(),
	loadScreen: new LoadScreen(),
	updateScheduler: updateScheduler,
	context: null,
	userSelection: [],
	handleRenderError(error, isFirstRender) {
		if (!isFirstRender) {
			this.updateScheduler.pause();
			alert(`The topology failed to refresh and will not be updated: ${error.message}`);
			return;
		}
		const $retryBtn = this.loadScreen.toErrorMessage(error.message);
		$retryBtn.on("click", async () => {
			this.loadScreen.toLoading();
			await this.render(true);
		});
	},
	async render(isFirstRender = false) {
		try {
			await this.renderWorker(isFirstRender);				
		} catch (error) {
			console.log(`[RENDER_ERROR] -> ${error.message}`);
			this.handleRenderError(error, isFirstRender);
		}
	},
	async renderWorker(isFirstRender) {
		const apiData = await getTopologyData(15000, 3);
		if(this.context) {
			this.updateTopology(apiData, isFirstRender);
		} else {
			this.createTopology(apiData, isFirstRender);
		}
		this.afterRender();
	},
	afterRender() {
		const { refreshEnabled } = this.userSettings;
		const { isRunning } = this.updateScheduler;
		if(refreshEnabled && !isRunning) {
			this.updateScheduler.start();
		} else if(!refreshEnabled && isRunning) {
			this.updateScheduler.pause();
		}
	},
	createTopology(apiData, isFirstRender) {
		this.context = new ConnectionData();
		this.context.build(apiData);
		this.renderTopology(isFirstRender, false);
		
		if(this.updateScheduler.isRunning) {
			return;
		}
		this.updateScheduler.setCallback(async () => {
			await this.render();
		});
		this.updateScheduler.start();
	},

	updateTopology(apiData, isFirstRender) {
		const { showInactive } = this.userSettings;
		const filteredData = ConnectionData.filterByStatus(
			apiData, showInactive
		);
		const hasChanged = this.context.refreshContext(filteredData);
		if(hasChanged) {
			this.renderTopology(isFirstRender, hasChanged);
		}
	},
	
	renderTopology(isFirstRender, hasChanged) {
		// d3 mutates edges for some reason, so clone it (trust me)
		const clonedEdges = this.context.edges.map((edge) => ({ ...edge }));	
		this.display.setAssetData(this.context, clonedEdges, this.userSelection)
		let alphaValue = 0;
		if(isFirstRender) {
			alphaValue = 1;
		} else if(hasChanged) {
			alphaValue = 0.1;
		}
		console.log(`Resulting Alpha Value: ${alphaValue}`);
		this.display.restartSimulation(alphaValue);
		
		if(isFirstRender) {
			this.loadScreen.hide();
			settingsUI.initialize(this);
		}
	},
	async toggleRefresh() {
		this.userSettings.refreshEnabled = !this.userSettings.refreshEnabled;
		if (this.userSettings.refreshEnabled) {
			await this.render();
		} else {
			this.updateScheduler.pause();
		}
	},
	async toggleInactive() {
		this.userSettings.showInactive = !this.userSettings.showInactive;
		await this.render();
	}
};

/**
 * @param {Number} timeout - refresh speed - 2,500 
 * @param {Number} retries 
 * @returns {Promise<Object[]>}
 */
async function getTopologyData(timeout = 15000, retries = 1) {
	if(retries > 5) {
		throw new Error("Use a lower value for retries allowed to avoid overloading the server");
	}
	const controller = new AbortController();
	const { signal } = controller;
	const timeoutId = setTimeout(() => controller.abort(), timeout);
	try {
		const response = await fetch("api/topology_data", { signal });
		if(!response.ok) {
			throw new Error(`Failed to fetch topology data: ${response.statusText}`);
		}
		const data = await response.json();
		if(!data || !data.nodes) {
			throw new Error("Invalid topology data received likely due to missing data");
		}
		clearTimeout(timeoutId);
		return data.nodes;
	} catch(err) {
		return onFetchError(err, timeout, retries, timeoutId);
	}
};

const onFetchError = async (err, timeout, retries, timeoutId) => {
	clearTimeout(timeoutId);
	let errorMsg = err.message;
	if(err.name === "AbortError") {
		errorMsg = "Timeout Error: the request to the API timed out after multiple attempts.";
		timeout += 5000; // timed out due to network issues -> increase timeout
	}
	if(retries <= 1) {
		throw new Error(errorMsg);
	}
	console.log(`[FETCH_ERROR] -> Request failed, ${retries - 1} attempts remaining`);
	// to avoid overloading server w/ reqs -v
	await new Promise((resolve) => setTimeout(resolve, 3000));
	return await getTopologyData(timeout, retries - 1);
};





