import {
	Field,
	Collapsible,
	ModalTab,
	COLLAPSE_STYLE,
	OptionGroup,
	SettingsToggler,
} from "./components/modal-assets.js";

const TAB_ICONS = Object.freeze({
	info: "fa-solid fa-info",
	settings: "fa-solid fa-gears",
	time: "fa-solid fa-clock-rotate-left",
});

const TOGGLER_ICONS = Object.freeze({
	DISPLAY: {
		enabled: "fa-regular fa-eye",
		disabled: "fa-regular fa-eye-slash",
	},
	CHECK: {
		enabled: "fas fa-check",
		disabled: "fas fa-times",
	},
	REFRESH: {
		enabled: "fa-regular fa-circle-play",
		disabled: "fa-regular fa-circle-pause",
	},
});

/**
 * @param {topology} topology
 * @returns {ModalTab[]}
 */
export function createSettingsModal(topology) {
	const overviewTab = new ModalTab("Topology Overview", TAB_ICONS.info);
	settingsBuilder.buildOverviewTab(topology, overviewTab);
	const preferenceTab = new ModalTab("Preferences", TAB_ICONS.settings);
	settingsBuilder.createPreferences(topology, preferenceTab);
	return [overviewTab, preferenceTab];
}

const settingUtils = {
	countActiveGroups(groupNodes, context) {
		let activeGroups = 0;
		groupNodes.forEach((group) => {
			const childNodes = context.filterBy(
				(node) => node.parentIdentifier === group.identifier
			);
			const activeCount =
				childNodes.filter((node) => node.isActive()).length || 0;
			activeGroups += +(activeCount > 0); // cast a bool to int, 999 iq
		});
		return activeGroups;
	},
	stringifyDate(date) {
		return new Date(date).toLocaleString();
	}



};

const settingsBuilder = {
	/**
	 * @param {topology} topology
	 * @param {ModalTab} overviewTab
	 */
	buildOverviewTab({ context, updateScheduler }, overviewTab) {
		const { lastUpdated, upTime } = updateScheduler;
		const activeCount = context.countActiveConnections();
		const groupNodes = context.filterBy((node) => node.isGroup());
		const activeGroups = settingUtils.countActiveGroups(
			groupNodes,
			context
		);
		overviewTab.addContent([
			Field.create("Total Connections", context.size),
			Field.create("Active Connections", activeCount),
			Field.create("Inactive Connections", context.size - activeCount),
			Field.create("Total Connection Groups", groupNodes.length),
			Field.create("Active Connection Groups", activeGroups),
		]);

		const $timeCollapsible = this.settingsTimeData(lastUpdated, upTime);
		overviewTab.addContent($timeCollapsible);
		settingsBuilder.overviewTabIntervals(overviewTab, updateScheduler);
	},
	/**
	 * ensures that no memory leaks occur with the intervals set
	 * @param {ModalTab} overviewTab
	 * @param {UserSettings} userSettings
	 * @param {updateScheduler} updateScheduler
	 */
	overviewTabIntervals(overviewTab, updateScheduler) {
		const { upTime } = updateScheduler;
		let uptimeInterval;
		overviewTab.setWhenVisible(() => {
			// ^- NOTE: this will also runs when the Modal Opens
			const { lastUpdated, delay } = updateScheduler;
			uptimeInterval = settingsBuilder.createUpTimeInterval(upTime);
			$("#last-updated-field").text(settingUtils.stringifyDate(lastUpdated));
			$("#refresh-countdown").text(
				settingUtils.stringifyDate(lastUpdated + delay)
			);
		});
		overviewTab.setWhenHidden(() => {
			// ^- NOTE: this will also runs when the Modal Closes
			if (uptimeInterval) {
				clearInterval(uptimeInterval);
			}
			uptimeInterval = null;
		});
	},
	settingsTimeData(lastUpdated, upTime, delay) {
		const uptimeCollapsible = new Collapsible(
			"Topology Time",
			COLLAPSE_STYLE.FOLDER
		);
		uptimeCollapsible.addHeaderIcon(TAB_ICONS.time);
		const upTimeString = new Date(upTime).toLocaleString();
		const startField = new Field("Topology Start", upTimeString);
		const uptimeField = new Field("Topology Uptime", upTimeString);
		const lastUpdatedField = new Field(
			"Last Update",
			new Date(lastUpdated).toLocaleString()
		);
		const refreshCountdown = new Field(
			"Next Update",
			new Date(lastUpdated + delay).toLocaleTimeString()
		);
		uptimeCollapsible.addContent([
			startField.toHTML(),
			lastUpdatedField.toHTML({ valueId: "last-updated-field" }),
			uptimeField.toHTML({ valueId: "uptime-field" }),
			refreshCountdown.toHTML({ valueId: "refresh-countdown" }),
		]);
		return uptimeCollapsible.$container;
	},
	createPreferences(topology, preferenceTab) {
		const { userSettings } = topology;
		const $container = $("<div>", { class: "settings-controls" });

		const toggleInactive = new SettingsToggler(
			"toggle-show-inactive",
			TOGGLER_ICONS.DISPLAY,
			"Show Inactive Nodes",
			userSettings.showInactive
		);
		toggleInactive.onTogglerClick(() => {
			topology.toggleInactive();
		});
		$container.append(toggleInactive.body);
		settingsBuilder.createToggleRefresh(topology, $container);
		preferenceTab.addContent($container);
		preferenceTab.setWhenVisible(() => {
			if(!topology.userSettings.refreshEnabled) {
				$("#speedOptionGroup").hide();
			}
		});
	},
	/**
	 * @param {topology} topology
	 * @param {JQuery<HTMLElement>} $container
	 */
	createToggleRefresh(topology, $container) {
		const { userSettings, updateScheduler } = topology;
		const toggleRefresh = new SettingsToggler(
			"toggle-enable-refresh",
			TOGGLER_ICONS.REFRESH,
			"Enable Refresh",
			userSettings.refreshEnabled
		);
		const speedOptions = [
			{ text: "Low", dataValue: "low" },
			{ text: "Medium", dataValue: "medium" },
			{ text: "High", dataValue: "high" },
		];

		const { stringDelay } = updateScheduler;
		const refreshOptions = new OptionGroup(
			"speedOptionGroup",
			"refresh-speeds",
			"speed-option"
		);
		refreshOptions.addOptions(speedOptions, stringDelay);
		refreshOptions.onOptionClick((speedOption) => {
			updateScheduler.setDelay(speedOption);
		});
		const $speedOptions = refreshOptions.body;
		toggleRefresh.onTogglerClick(() => {
			topology.toggleRefresh();
			if (userSettings.refreshEnabled) {
				$speedOptions.slideDown(300);
			} else {
				$speedOptions.slideUp(300);
			}
		});
		$container.append(toggleRefresh.body, $speedOptions);
	},
	/**
	 * creates and returns interval ID for the uptime timer
	 * @param {Date} startTime 
	 * @returns {number} 
	 */
	createUpTimeInterval(startTime) {
		const pad = (num) => (num < 10 ? `0` + num : num);
		const uptimeId = setInterval(() => {
			const elapsed = Math.floor((Date.now() - startTime) / 1000);
			const hours = Math.floor(elapsed / 3600);
			const minutes = Math.floor((elapsed % 3600) / 60);
			const seconds = elapsed % 60;
			$("#uptime-field").text(`${pad(hours)}:${pad(minutes)}:${pad(seconds)}`);
		}, 1000);
		return uptimeId;
	},
};