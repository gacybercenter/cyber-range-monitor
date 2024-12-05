import { Field, Collapsible, ModalTab, modalIcons, collapseStyle } from "./components/modal-assets.js";
import { renderGroupSelector } from "./components/group-select.js";
import { createNodeControls, buttonTemplates, buttonEvents } from "./components/node-btns.js";


const { GENERAL_ICONS, FIELD_ICONS } = modalIcons;

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

		const controlsCollapse = new Collapsible("Controls", collapseStyle.FOLDER);
		controlsCollapse.addHeaderIcon(GENERAL_ICONS.gear);
		const nodeControls = createNodeControls(selection);
		controlsCollapse.addContent(nodeControls);

		generalTabData.addContent(controlsCollapse.$container);
		return [generalTabData];
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
		const controlsCollapse = new Collapsible("Controls", collapseStyle.FOLDER);
		controlsCollapse.addHeaderIcon(GENERAL_ICONS.gear);
		const nodeControls = createNodeControls([identifier]); // <- you must pass a list
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
			selection.filter((node) => node.dump.activeConnections > 0).length || 0;

		overviewTab.addContent([
			Field.create("Connections Selected", selection.length, {
				fasIcon: FIELD_ICONS.userGroup,
			}),
			Field.create("Active Connections", activeCount)
				.toHTML({ 
					fasIcon: activeCount > 0 ? FIELD_ICONS.online : FIELD_ICONS.offline
				})
		]);
		const childCollapsible = new Collapsible("Selected Connection(s)", collapseStyle.FOLDER);
		childCollapsible.addHeaderIcon(GENERAL_ICONS.magnify);
		selection.forEach((connection) => {
			const overviewCollapse = new Collapsible(connection.name, collapseStyle.THUMBTACK);
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
			childNodes.filter((node) => {
				return node.dump.activeConnections > 0;
			}).length || 0;

		groupTab.addTabId("groupOverview");

		groupTab.addContent([
			Field.create("Group Name", name, { fasIcon: FIELD_ICONS.pen }),
			Field.create("Group Identifier", identifier, { fasIcon: FIELD_ICONS.id }),
			Field.create("Group Type", dump.type || "Not set", { fasIcons: FIELD_ICONS.wrench }),
			Field.create("Child Connections", childNodes.length, { fasIcon: FIELD_ICONS.userGroup }),
			Field.create("Active Child Connections", activeCount, { fasIcon: FIELD_ICONS.online }),
			Field.create(
				"Inactive Child Connections",
				childNodes.length - activeCount,
				{ fasIcon: FIELD_ICONS.offline }
			),
			Field.create("Group Status", activeCount > 0 ? "Online" : "Offline"),
		]);

		if (Object.hasOwn(connGroup, "parentIdentifier")) {
			const parent = nodeMap.get(connGroup.parentIdentifier);
			if (parent) {
				tabAssets.initParentInfo(parent, groupTab);
			}
		}
		const childSummary = new Collapsible(
			`Child Connections (${childNodes.length})`,
			collapseStyle.FOLDER
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
			Field.create("Parent Identifier", identifier, { fasIcon: FIELD_ICONS.parentId }),
		]);
	},
	nodeOverview(connection) {
		const { name, identifier, dump } = connection;
		return [
			Field.create("Name", name, { fasIcon: FIELD_ICONS.pen }),
			Field.create("Identifier", identifier, { fasIcon: FIELD_ICONS.id }),
			Field.create("Protocol", dump.protocol || "Unknown", { fasIcon: FIELD_ICONS.protocol }),
		];
	},
	/**
	 * @param {string} message 
	 * @returns {JQuery<HTMLElement>}
	 */
	warning(message) {
		return Field.create("Note", message, { fasIcon: GENERAL_ICONS.warn });
	}
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
		const selectorTab = new ModalTab("Group Controls", FIELD_ICONS.wrench);
		selectorTab.addTabId("groupSelector");
		const { $content, groupSelector } = renderGroupSelector(childConnections);
		selectorTab.addContent($content);
		const $nodeBtns = selectorBuilder.initControls(groupSelector);
		selectorTab.addContent($nodeBtns);
		return selectorTab;
	},
	/**
	 * @param {GroupSelector} groupSelector 
	 * @returns {JQuery<HTMLElement>} 
	 */
	initControls(groupSelector) {
		const buttonOff = (controlBtn) => {
			if (controlBtn.isDisabled()) {
				controlBtn.errorAnimate();
				return true;
			}
			return false;
		};

		const nodeControls = new Collapsible("Control Selection", collapseStyle.FOLDER);
		nodeControls.addHeaderIcon(GENERAL_ICONS.gear);

		const connect = buttonTemplates.createConnect();
		connect.addClickEvent(() => {
			if(buttonOff(connect)) {
				return;
			}
			const { checkedIds } = groupSelector;
			if (checkedIds.length === 0) {
				alert("No connections selected to connect to, try again");
				return;
			}
			console.log("[GROUP_SELECT] Connecting To: ", checkedIds);
			buttonEvents.connectClick(checkedIds, connect);
		});

		const kill = buttonTemplates.createKill();
		kill.addClickEvent(() => {
			if(buttonOff(kill)) {
				return;
			}
			const { checkedIds } = groupSelector;
			if (checkedIds.length === 0) {
				alert("No connections were selected to kill, try again");
				return;
			}
			console.log("[GROUP_SELECT] Killing: ", checkedIds);
			buttonEvents.killClick(checkedIds, kill);
		});

		const timeline = buttonTemplates.createTimeline();
		timeline.addClickEvent(() => {
			if(buttonOff(timeline)) {
				return;
			}
			const { checkedIds } = groupSelector;
			if (checkedIds.length !== 1) {
				alert("The timeline can only be viewed for a single connection.");
				return;
			}
			buttonEvents.timelineClick(checkedIds, timeline);
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
		const attrCollapse = new Collapsible("Attributes", collapseStyle.THUMBTACK);
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
		const collapse = new Collapsible("Connectivity", collapseStyle.THUMBTACK);
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
			Field.create("Connection Status", status || "Not available", { fasIcon: statusIcon }),
			Field.create("Active Connections", activeConnections || 0, { fasIcon: FIELD_ICONS.active }),
			Field.create("Protocol", protocol || "Not available", { fasIcon: FIELD_ICONS.protocol }),
			Field.create("Last Active", lastOnline || "Not available", { fasIcon: FIELD_ICONS.date }),
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
		const hasProfiles = (profileCount > 0);

		const sharingCollapse = new Collapsible(
			`Sharing Profiles (${profileCount})`,
			(hasProfiles)? collapseStyle.FOLDER : collapseStyle.THUMBTACK
		);
		sharingCollapse.addHeaderIcon(FIELD_ICONS.userGroup);
		if(!hasProfiles) {
			sharingCollapse.addContent(
				tabAssets.warning("No sharing profiles were found for this connection")
			)
			return sharingCollapse.$container;
		}
		
		sharingProfiles.forEach((profile) => {
			const collapse = new Collapsible(profile.name ?? "Unamed Profile", collapseStyle.THUMBTACK);
			collapse.addHeaderIcon(FIELD_ICONS.user);
			detailsBuilder.initProfile(profile, collapse);
			sharingCollapse.addContent(profileInfo);
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
					`${key} (stringified)`,
					JSON.stringify(current)
				);
			} else {
				newField = Field.create(key, current);
			}
			profileCollapse.addContent(newField);
		});
	},
};
