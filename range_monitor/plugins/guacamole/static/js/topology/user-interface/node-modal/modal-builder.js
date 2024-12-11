import {
	Field,
	Collapsible,
	ModalTab,
	MODAL_ICONS,
	COLLAPSE_STYLE,
} from "./components/modal-assets.js";
import {
	NODE_CONTROLS,
	NodeControl,
	createAllControls,
	controlEvents,
} from "./components/node-btns.js";
import { renderGroupSelector } from "./components/group-select.js";

const { GENERAL_ICONS, FIELD_ICONS } = MODAL_ICONS;
export const modalTypes = {
	/**
	 * a modal for when the user has clicked on a single connection
	 * @param {ConnectionNode} connection
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab[]}
	 */
	singleConnection(connection, nodeMap) {
		const summaryTab = tabBuilder.nodeSummary(connection, nodeMap);
		const detailsTab = tabBuilder.singleNodeDetails(connection);
		return [summaryTab, detailsTab];
	},
	/**
	 * @summary
	 * a modal when the user has selected multiple leaf connections,
	 * not a group
	 * @param {ConnectionNode[]} selection
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab[]}
	 */
	manyConnections(selection, nodeMap) {
		const selectedConns = selection.map((ids) => nodeMap.get(ids));
		const generalTabData = tabBuilder.connectionsOverview(
			selectedConns,
			nodeMap
		);

		const controlsCollapse = new Collapsible("Controls", COLLAPSE_STYLE.FOLDER);
		controlsCollapse.addHeaderIcon(GENERAL_ICONS.gear);
		const nodeControls = createAllControls(selection);
		controlsCollapse.addContent(nodeControls);

		generalTabData.addContent(controlsCollapse.$container);
		return [generalTabData]; // <- modal requires an array, no matter tab size
	},
	/**
	 * @summary
	 * a modal for when the user has selected a connection group,
	 * only 1 should ever be displayed at once.
	 * @param {ConnectionNode} connGroup
	 * @param {ConnectionNode[]} nodes
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab[]}
	 */
	connectionGroup(connGroup, nodes, nodeMap) {
		const childNodes = nodes.filter(
			(node) => node.parentIdentifier === connGroup.identifier
		);
		const overviewTabData = tabBuilder.groupOverviewTab(
			connGroup,
			childNodes,
			nodeMap
		);
		const controlsTabData = selectorBuilder.init(childNodes);
		return [overviewTabData, controlsTabData];
	},
};

const tabBuilder = {
	/**
	 * @param {ConnectionNode} connection
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab}
	 */
	nodeSummary(connection, nodeMap) {
		const summaryTab = new ModalTab("Summary", GENERAL_ICONS.summary);
		summaryTab.addTabId("summaryTab");
		const { identifier, parentIdentifier } = connection;
		const nodeOverview = tabAssets.nodeOverview(connection);
		summaryTab.addContent(nodeOverview);
		const parent = nodeMap.get(parentIdentifier);
		if (parent) {
			tabAssets.initParentInfo(parent, summaryTab);
		}
		const controlsCollapse = new Collapsible("Controls", COLLAPSE_STYLE.FOLDER);
		controlsCollapse.addHeaderIcon(GENERAL_ICONS.gear);
		const nodeControls = createAllControls([identifier]); // <- must be passed as a list
		controlsCollapse.addContent(nodeControls);
		summaryTab.addContent(controlsCollapse.$container);
		return summaryTab;
	},
	/**
	 * @param {ConnectionNode} connection
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab}
	 */
	singleNodeDetails(connection) {
		const detailsTab = new ModalTab("Details", GENERAL_ICONS.info);
		detailsTab.addTabId("detailsTab");
		const detailsContent = detailsBuilder.init(connection, detailsTab);
		detailsTab.addContent(detailsContent);
		return detailsTab;
	},
	/**
	 * @param {ConnectionNode[]} selection
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab}
	 */
	connectionsOverview(selection) {
		const overviewTab = new ModalTab("Overview", GENERAL_ICONS.summary);
		overviewTab.addTabId("overviewTab");
		const activeCount =
			selection.filter((node) => {
				return node.dump.activeConnections > 0;
			}).length || 0;

		overviewTab.addContent([
			Field.create("Connections Selected", selection.length, {
				fasIcon: FIELD_ICONS.userGroup,
			}),
			Field.create("Active Connections", activeCount).toHTML({
				fasIcon: activeCount > 0 ? FIELD_ICONS.online : FIELD_ICONS.offline,
			}),
		]);

		const childCollapsible = new Collapsible(
			"Selected Connection(s)",
			COLLAPSE_STYLE.FOLDER
		);
		childCollapsible.addHeaderIcon(GENERAL_ICONS.magnify);

		selection.forEach((connection) => {
			const overviewCollapse = new Collapsible(
				connection.name,
				COLLAPSE_STYLE.DEFAULT
			);
			const nodeOverview = tabAssets.nodeOverview(connection);
			overviewCollapse.addContent(nodeOverview);
			childCollapsible.addContent(overviewCollapse.$container);
		});
		overviewTab.addContent(childCollapsible.$container);
		return overviewTab;
	},
	/**
	 * @param {ConnectionNode} connGroup
	 * @param {ConnectionNode[]} childNodes
	 * @param {Map<string, ConnectionNode>} nodeMap
	 * @returns {ModalTab}
	 */
	groupOverviewTab(connGroup, childNodes, nodeMap) {
		const { name, identifier, dump } = connGroup;
		const groupTab = new ModalTab("Group Details", FIELD_ICONS.userGroup);

		const activeCount =
			childNodes.filter((node) => node.isActive()).length || 0;

		groupTab.addTabId("groupOverview");
		const groupIsOnline = activeCount > 0;
		groupTab.addContent([
			Field.create("Group Name", name, { fasIcon: FIELD_ICONS.pen }),
			Field.create("Group Identifier", identifier, { fasIcon: FIELD_ICONS.id }),
			Field.create("Group Type", dump.type || "Not set", {
				fasIcons: FIELD_ICONS.wrench,
			}),
			Field.create("Child Connections", childNodes.length, {
				fasIcon: FIELD_ICONS.userGroup,
			}),
			Field.create("Active Child Connections", activeCount, {
				fasIcon: FIELD_ICONS.online,
			}),
			Field.create(
				"Inactive Child Connections",
				childNodes.length - activeCount,
				{ fasIcon: FIELD_ICONS.offline }
			),
			Field.create("Group Status", groupIsOnline ? "Online" : "Offline", {
				fasIcon: groupIsOnline ? FIELD_ICONS.online : FIELD_ICONS.offline,
			}),
		]);

		if (Object.hasOwn(connGroup, "parentIdentifier")) {
			const parent = nodeMap.get(connGroup.parentIdentifier);
			if (parent) {
				tabAssets.initParentInfo(parent, groupTab);
			}
		}
		const childSummary = new Collapsible(
			`Child Connections (${childNodes.length})`,
			COLLAPSE_STYLE.FOLDER
		);
		childNodes.forEach((child) => {
			const field = Field.create(child.name, `(${child.identifier})`, {
				fasIcon: FIELD_ICONS.laptop,
			});
			childSummary.addContent(field);
		});

		groupTab.addContent(childSummary.$container);
		return groupTab;
	},
};

const tabAssets = {
	/**
	 * @param {ConnectionNode} parent
	 * @param {ModalTab} modalTab
	 */
	initParentInfo(parent, modalTab) {
		const { name, identifier } = parent;
		modalTab.addContent([
			Field.create("Parent Connection", name, { fasIcon: FIELD_ICONS.parent }),
			Field.create("Parent Identifier", identifier, {
				fasIcon: FIELD_ICONS.parentId,
			}),
		]);
	},
	nodeOverview(connection) {
		const { name, identifier, dump } = connection;
		return [
			Field.create("Name", name, { fasIcon: FIELD_ICONS.pen }),
			Field.create("Identifier", identifier, { fasIcon: FIELD_ICONS.id }),
			Field.create("Protocol", dump.protocol || "Unknown", {
				fasIcon: FIELD_ICONS.protocol,
			}),
		];
	},
	/**
	 * @param {string} message
	 * @returns {JQuery<HTMLElement>}
	 */
	warning(message) {
		return Field.create("Note", message, { fasIcon: GENERAL_ICONS.warn });
	},
};

/**
 * creates the group selector in the modal
 */
const selectorBuilder = {
	/**
	 * @param {ConnectionNode[]} childConnections
	 * @returns {ModalTab}
	 */
	init(childConnections) {
		const selectorTab = new ModalTab("Manage Group", FIELD_ICONS.wrench);
		selectorTab.addTabId("groupSelector");
		const groupSelector = renderGroupSelector(childConnections);
		selectorTab.addContent(groupSelector.$content);
		const $nodeBtns = selectorBuilder.initControls(groupSelector);
		selectorTab.addContent($nodeBtns);
		return selectorTab;
	},
	/**
	 * @param {GroupSelector} groupSelector
	 * @returns {JQuery<HTMLElement>}
	 */
	initControls(groupSelector) {
		const nodeControls = new Collapsible(
			"Control Selection",
			COLLAPSE_STYLE.FOLDER
		);
		nodeControls.addHeaderIcon(GENERAL_ICONS.gear);
		const errorOnNoSelection = (button, callback) => {
			return () => {
				const { checkedIds } = groupSelector;
				if (checkedIds.length === 0) {
					alert(`No connections were selected to ${button.text}`);
					button.errorAnimate();
					return;
				}
				callback(checkIds);
			};
		};
		const connect = new NodeControl(NODE_CONTROLS.CONNECT);
		connect.onClick(errorOnNoSelection(connect, controlEvents.connectToNodes));
		const kill = new NodeControl(NODE_CONTROLS.KILL);
		kill.onClick(errorOnNoSelection(kill, controlEvents.killNodes));

		const timeline = new NodeControl(NODE_CONTROLS.TIMELINE, () => {
			if (groupSelector.checkedIds.length === 1) {
				controlEvents.viewTimeline(groupSelector.checkedIds);
			} else {
				alert("Only one connection can be viewed at a time");
			}
		});
		nodeControls.addContent([connect.$tag, kill.$tag, timeline.$tag]);
		return nodeControls.$container;
	},
};

/**
 * @summary
 * abstracted static object containing
 * methods related to building HTML for the connection
 * details the single connection Modal
 */
const detailsBuilder = {
	/**
	 * @summary
	 * abstracted method for building the
	 * connection details, call this to create the collapsible
	 * @param {ConnectionNode} connection
	 * @param {ModalTab} detailsTab
	 * @returns {JQuery<HTMLElement>} - the collapsible with all connection details
	 */
	init(connection, detailsTab) {
		const { dump } = connection; // raw json data
		const $attributes = detailsBuilder.getAttributes(dump);
		const $connectivity = detailsBuilder.getConnectivity(dump);
		const $sharing = detailsBuilder.getSharingProfiles(dump);
		detailsTab.addContent([$attributes, $connectivity, $sharing]);
	},
	/**
	 * @param {Object} connectionDump
	 * @returns {JQuery<HTMLElement>}
	 */
	getAttributes(connectionDump) {
		const { attributes } = connectionDump;
		const attrCollapse = new Collapsible("Attributes", COLLAPSE_STYLE.DEFAULT);
		attrCollapse.addHeaderIcon(GENERAL_ICONS.info);
		if (!attributes) {
			attrCollapse.addContent(
				Field.create("Note", "No attributes have been set for this connection")
			);
			return attrCollapse.$container;
		}

		Object.keys(attributes).forEach((key) => {
			const stringAttr = attributes[key] ?? "Not set";
			attrCollapse.addContent(Field.create(key, stringAttr));
		});

		return attrCollapse.$container;
	},
	/**
	 * @param {Object} connectionDump
	 */
	getConnectivity(connectionDump) {
		const { activeConnections, lastActive, protocol } = connectionDump;
		const collapse = new Collapsible("Connectivity", COLLAPSE_STYLE.DEFAULT);
		collapse.addHeaderIcon(FIELD_ICONS.active);

		let status = "Online";
		let statusIcon = FIELD_ICONS.online;
		if (!activeConnections || activeConnections < 0) {
			status = "Offline";
			statusIcon = FIELD_ICONS.offline;
		}

		let lastOnline = "N/A";
		if (lastActive) {
			lastOnline = new Date(lastActive).toUTCString();
		}

		collapse.addContent([
			Field.create("Connection Status", status || "Not available", {
				fasIcon: statusIcon,
			}),
			Field.create("Active Connections", activeConnections || 0, {
				fasIcon: FIELD_ICONS.active,
			}),
			Field.create("Protocol", protocol || "Not available", {
				fasIcon: FIELD_ICONS.protocol,
			}),
			Field.create("Last Active", lastOnline || "Not available", {
				fasIcon: FIELD_ICONS.date,
			}),
		]);
		return collapse.$container;
	},
	/**
	 * @param {ConnectionNode} connection
	 * @returns {JQuery<HTMLElement>}
	 */
	getSharingProfiles(connectionDump) {
		const { sharingProfiles } = connectionDump;
		const profileCount = sharingProfiles ? sharingProfiles.length : 0;
		const hasProfiles = profileCount > 0;

		const sharingCollapse = new Collapsible(
			`Sharing Profiles (${profileCount})`,
			hasProfiles ? COLLAPSE_STYLE.FOLDER : COLLAPSE_STYLE.THUMBTACK
		);

		sharingCollapse.addHeaderIcon(FIELD_ICONS.userGroup);
		if (!hasProfiles) {
			sharingCollapse.addContent(
				tabAssets.warning("No sharing profiles were found for this connection")
			);
			return sharingCollapse.$container;
		}

		sharingProfiles.forEach((profile) => {
			const collapse = new Collapsible(
				profile.name ?? "Unamed Profile",
				COLLAPSE_STYLE.DEFAULT
			);
			collapse.addHeaderIcon(FIELD_ICONS.user);
			detailsBuilder.initProfile(profile, collapse);
			sharingCollapse.addContent(collapse.$container);
		});
		return sharingCollapse.$container;
	},
	/**
	 * @param {Object} profileDump - single object in the sharingProfiles array
	 * @param {Collapsible} profileCollapse - the collapsible to hold the info
	 * @returns {JQuery<HTMLElement>} - the container of the rendered profile collapsible
	 */
	initProfile(profileDump, profileCollapse) {
		if (!profileDump || Object.keys(profileDump).length === 0) {
			profileCollapse.addContent(
				tabAssets.warning("No data was found for this profile")
			);
			return;
		}
		Object.keys(profileDump).forEach((key) => {
			const current = profileDump[key];
			let newField;
			if (!current) {
				newField = Field.create(key, "Unset");
			} else if (typeof current === "object") {
				newField = Field.create(
					`${key}`,
					JSON.stringify(current),
					FIELD_ICONS.wrench
				);
			} else {
				newField = Field.create(key, current);
			}
			profileCollapse.addContent(newField);
		});
	},
};
