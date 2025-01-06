import {
	Field,
	Collapsible,
	ModalTab,
	COLLAPSE_STYLE,
	OptionGroup,
	SettingsToggler,
	MODAL_ICONS,
} from "./components/modal-assets.js";
export { SETTINGS, createSettingsModal };

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

const SETTINGS = Object.freeze({
	LABEL: {
		SHOW_ALL: "show-all",
		HIDE_ALL: "hide-all",
		HIDE_INACTIVE: "hide-inactive",
	},
	ICON: {
		USE_OS: "use-os",
		USE_ACTIVE_COUNT: "use-count",
	},
	REFRESH_SPEED: {
		LOW: "low",
		MEDIUM: "medium",
		HIGH: "high",
	},
	RETRIES: {
		NONE: "none",
		SOME: "three",
		FORGIVING: "forgiving",
	},
});

/**
 * @param {topology} topology
 * @returns {ModalTab[]}
 */
function createSettingsModal(topology) {
	const overviewTab = new ModalTab("Topology Overview", TAB_ICONS.info);
	settingsTabBuilder.buildOverviewTab(topology, overviewTab);
	const visibilityTab = controlBuilder.createVisibilityControls(topology);
	const refreshTab = refreshBuilder.createRefreshTab(topology);
	return [overviewTab, visibilityTab, refreshTab];
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
	},
};

const settingsTabBuilder = {
	/**
	 * @param {topology} topology
	 * @param {ModalTab} overviewTab
	 */
	buildOverviewTab({ context, updateScheduler }, overviewTab) {
		const { lastUpdated, upTime } = updateScheduler;
		const activeCount = context.countActiveConnections();
		const groupNodes = context.filterBy((node) => node.isGroup());
		const activeGroups = settingUtils.countActiveGroups(groupNodes, context);
		overviewTab.addContent([
			Field.create("Total Connections", context.size),
			Field.create("Active Connections", activeCount),
			Field.create("Inactive Connections", context.size - activeCount),
			Field.create("Total Connection Groups", groupNodes.length),
			Field.create("Active Connection Groups", activeGroups),
		]);

		const $timeCollapsible = this.settingsTimeData(lastUpdated, upTime);
		overviewTab.addContent($timeCollapsible);
		settingsTabBuilder.overviewTabIntervals(overviewTab, updateScheduler);
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
			const { lastUpdated, delay } = updateScheduler;
			uptimeInterval = settingsTabBuilder.createUpTimeInterval(upTime);
			$("#last-updated-field").text(settingUtils.stringifyDate(lastUpdated));
			$("#refresh-countdown").text(
				settingUtils.stringifyDate(lastUpdated + delay)
			);
		});
		overviewTab.setWhenHidden(() => {
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

const controlBuilder = {
	/**
	 * @returns {ModalTab}
	 */
	createVisibilityControls(topology) {
		const { userSettings } = topology;
		const toggleInactive = new SettingsToggler(
			"toggle-show-inactive",
			TOGGLER_ICONS.DISPLAY,
			"Show Inactive Nodes",
			userSettings.showInactive
		);
		toggleInactive.onTogglerClick(() => {
			topology.toggleInactive();
		});
		const labelControls = this.createLabelControls(topology);
		const iconControls = this.createIconControls(topology);
		const visibilityTab = new ModalTab(
			"Visibility Controls",
			MODAL_ICONS.GENERAL_ICONS.magnify
		);
		visibilityTab.addContent([
			toggleInactive.body,
			labelControls,
			iconControls,
		]);
		return visibilityTab;
	},
	createLabelControls(topology) {
		const { userSettings } = topology;
		const { LABEL } = SETTINGS;
		const labelsCollapse = new Collapsible(
			"Label Preferences",
			COLLAPSE_STYLE.DEFAULT
		);

		const labelsGroup = new OptionGroup(
			"labelOptions",
			"label-preferences",
			"label-option"
		);
		const labelControls = [
			{ text: "Show all Labels", dataValue: LABEL.SHOW_ALL },
			{ text: "Hide Inactive Labels", dataValue: LABEL.HIDE_INACTIVE },
			{ text: "Hide All Labels", dataValue: LABEL.HIDE_ALL },
		];
		labelsGroup.addOptions(labelControls, userSettings.labelPreference);
		labelsGroup.onOptionClick((selected) => {
			userSettings.labelPreference = selected;
			console.log("Selected Label Preference: ", selected);
		}, userSettings.canChangeLabel);
		labelsCollapse.addContent(labelsGroup.body);
		return labelsCollapse.$container;
	},
	createIconControls(topology) {
		const { userSettings } = topology;
		const { ICON } = SETTINGS;
		const iconGroup = new OptionGroup(
			"iconOptions",
			"icon-preferences",
			"icon-option"
		);
		iconGroup.addOptions(
			[
				{ text: "Use OS Icons", dataValue: ICON.USE_OS },
				{ text: "Use Active Count Icons", dataValue: ICON.USE_ACTIVE_COUNT },
			],
			userSettings.iconPreference
		);
		iconGroup.onOptionClick((selected) => {
			userSettings.iconPreference = selected;
			console.log("Selected Icon Preference: ", selected);
		});
		const iconCollapse = new Collapsible(
			"Icon Preferences",
			COLLAPSE_STYLE.DEFAULT
		);
		iconCollapse.addContent(iconGroup.body);
		return iconCollapse.$container;
	},
};

const refreshBuilder = {
	createRefreshTab(topology) {
		const { userSettings, updateScheduler } = topology;
		const toggleRefresh = new SettingsToggler(
			"toggle-enable-refresh",
			TOGGLER_ICONS.REFRESH,
			"Enable Refresh",
			userSettings.refreshEnabled
		);
		toggleRefresh.onTogglerClick(() => {
			topology.toggleRefresh();
		});
		const refreshRate = this.createRefreshSpeeds(userSettings, updateScheduler);
		const allowedRetries = this.createAllowedRetries(userSettings);
		const tab = new ModalTab("Refresh Controls", TAB_ICONS.settings);
		tab.addContent([
			toggleRefresh.body,
			refreshRate,
			allowedRetries,
		]);
		return tab;
	},
	createRefreshSpeeds(userSettings, updateScheduler) {
		const speedOptionCollapse = new Collapsible(
			"Topology Refresh Rate",
			COLLAPSE_STYLE.FOLDER
		);
		speedOptionCollapse.addHeaderIcon(TAB_ICONS.time);

		const { REFRESH_SPEED } = SETTINGS;
		const speedOptions = [
			{ text: "Low", dataValue: REFRESH_SPEED.LOW },
			{ text: "Medium", dataValue: REFRESH_SPEED.MEDIUM },
			{ text: "High", dataValue: REFRESH_SPEED.HIGH },
		];

		const refreshOptions = new OptionGroup(
			"speedOptionGroup",
			"refresh-speeds",
			"speed-option"
		);
		refreshOptions.addOptions(speedOptions, userSettings.refreshSpeed);
		refreshOptions.onOptionClick((speedOption) => {
			updateScheduler.setDelay(speedOption);
			userSettings.refreshSpeed = speedOption;
		});
		speedOptionCollapse.addContent(refreshOptions.body);
		return speedOptionCollapse.$container;
	},
	createAllowedRetries(userSettings) {
		const { RETRIES } = SETTINGS;
		const retryGroup = new OptionGroup(
			"retryOptionGroup",
			"retry-options",
			"retry-option"
		);
		retryGroup.addOptions([
			{ text: "None (0)", dataValue: RETRIES.NONE },
			{ text: "Some (3)", dataValue: RETRIES.SOME },
			{ text: "Forgiving (5)", dataValue: RETRIES.FORGIVING },
		], userSettings.allowedRetries);
		retryGroup.onOptionClick((selected) => {
			userSettings.allowedRetries = selected;
			console.log("Selected Retry Option: ", selected);
		});
		const retriesCollapse = new Collapsible(
			"Allowed Retries",
			COLLAPSE_STYLE.FOLDER
		);
		retriesCollapse.addHeaderIcon(MODAL_ICONS.GENERAL_ICONS.summary);
		retriesCollapse.addContent(retryGroup.body);
		return retriesCollapse.$container;
	},
};