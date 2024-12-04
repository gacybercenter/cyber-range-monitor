import { Field, Collapsible, ModalTab } from "./components/modal-assets.js";
import { renderGroupSelector } from "./components/group-select.js";
import {
	createNodeControls,
	buttonTemplates,
	buttonEvents,
} from "./components/node-btns.js";



/**
 * @enum {string}
 * icons that appear in fields
 * and tabs 
 */
const generalIcons = {
	chartLine: "fa-solid fa-chart-line",
	summary: "fa-solid fa-list",
	gear: "fa-solid fa-gears",
	info: "fa-solid fa-circle-info",
	magnify: "fa-solid fa-magnifying-glass-chart",
	thumbtack: "fa-solid fa-thumbtack",
};

/**
 * @enum {string}
 * icons that appear in fields 
 */
const fieldIcons = {
	id: "fa-regular fa-address-card",
	parentId: "fa-solid fa-passport",
	parent: "fa-solid fa-network-wired",
	active: "fa-solid fa-wifi",
	offline: "fa-solid fa-plug-circle-minus off-icon",
	online: "fa-solid fa-plug-circle-plus on-icon",
	userGroup: "fa-solid fa-users",
	wrench: "fa-solid fa-wrench",
	protocol: "fa-solid fa-satellite-dish",
	date: "fa-regular fa-calendar",
};



export const modalTypes = {
	/**
	 * @summary
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

		const controlsCollapse = new Collapsible("Node Controls");
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
		const summaryTab = new ModalTab("Summary", generalIcons.summary);
		summaryTab.addTabId("summaryTab");
		const { identifier, parentIdentifier } = connection;
		const nodeOverview = tabAssets.nodeOverview(connection);
		summaryTab.addContent(nodeOverview);
		const parent = nodeMap.get(parentIdentifier);
		if (parent) {
			tabAssets.initParentInfo(parent, summaryTab);
		}
		const controlsCollapse = new Collapsible("Node Controls");
		controlsCollapse.addHeaderIcon(generalIcons.gear);
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
		const detailsTab = new ModalTab("Details", generalIcons.info);
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
		const overviewTab = new ModalTab("Overview", generalIcons.summary);
		overviewTab.addTabId("overviewTab");
		const activeCount =
			selection.filter((node) => node.dump.activeConnections > 0).length || 0;

		overviewTab.addContent([
			Field.create("Connections Selected", selection.length),
			Field.create("Active Connections", activeCount)
				.toHTML({ 
					fasIcon: activeCount > 0 ? fieldIcons.online : fieldIcons.offline
				})
		]);
		const childCollapsible = new Collapsible("Selected Connection(s)");
		childCollapsible.addHeaderIcon(generalIcons.magnify);

		selection.forEach((connection) => {
			const nodeOverview = tabAssets.nodeOverview(connection);
			childCollapsible.addContent(nodeOverview);
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
		const groupTab = new ModalTab("Group Details", fieldIcons.userGroup);
		const activeCount =
			childNodes.filter((node) => {
				return node.dump.activeConnections > 0;
			}).length || 0;

		groupTab.addTabId("groupOverview");

		groupTab.addContent([
			Field.create("Group Name", name),
			Field.create("Group Identifier", identifier),
			Field.create("Group Type", dump.type || "Not set"),
			Field.create("Child Connections", childNodes.length),
			Field.create("Active Child Connections", activeCount),
			Field.create(
				"Inactive Child Connections",
				childNodes.length - activeCount
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
			`Child Connection(s) Summary (${childNodes.length})`
		);

		childNodes.forEach((child) => {
			childSummary.addContent(
				Field.create(child.name, `(${child.identifier})`)
			);
		});

		groupTab.addContent(childSummary.$container);
		return groupTab;
	},
};

const tabAssets = {
	initParentInfo(parent, modalTab) {
		const { name, identifier } = parent;
		modalTab.addContent([
			Field.create("Parent Connection", name),
			Field.create("Parent Identifier", identifier),
		]);
	},
	/**
	 * creates the "connect", "kill", and "timeline"
	 * button tab, do not use for Connection Groups
	 * (seperate logic)
	 * @param {string[]} selectedIds
	 * @param {boolean} includeTimeline - false for many connections
	 * @returns {ModalTab}
	 */
	initNodeButtons(selectedIds) {
		const controlsTab = new ModalTab("Controls", generalIcons.gear);
		controlsTab.addTabId("controlsTab");
		const controlBtns = createNodeControls(selectedIds);
		controlsTab.addContent(controlBtns);
		return controlsTab;
	},

	nodeOverview(connection) {
		const { name, identifier, dump } = connection;
		return [
			Field.create("Name", name),
			Field.create("Identifier", identifier),
			Field.create("Protocol", dump.protocol || "Unknown"),
		];
	},
};

/**
 * creates the group selector in the modal
 */
const selectorBuilder = {
	init(childConnections) {
		const selectorTab = new ModalTab("Group Controls", generalIcons.wrench);
		selectorTab.addTabId("groupSelector");
		const { $content, groupSelector } = renderGroupSelector(childConnections);
		selectorTab.addContent($content);
		const $nodeBtns = selectorBuilder.initControls(groupSelector);
		selectorTab.addContent($nodeBtns);
		return selectorTab;
	},
	initControls(groupSelector) {
		const nodeControls = new Collapsible("Control Selection");
		const connect = buttonTemplates.createConnect();
		
		connect.$tag.on("click", () => {
			if(connect.isDisabled()) {
				connect.errorAnimate();
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
		kill.$tag.on("click", () => {
			if(kill.isDisabled()) {
				kill.errorAnimate();
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
		timeline.$tag.on("click", () => {
			if(timeline.isDisabled()) {
				timeline.errorAnimate();
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
		const attrCollapse = new Collapsible("Attributes");
		attrCollapse.addHeaderIcon(generalIcons.thumbtack)
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
		const collapse = new Collapsible("Connectivity");
		collapse.addHeaderIcon(fieldIcons.active);

		let status = "Online";
		if (!activeConnections || activeConnections < 0) {
			status = "Offline";
		}

		let lastOnline = "Not available";
		if (lastActive) {
			lastOnline = new Date(lastActive).toUTCString();
		}

		collapse.addContent([
			Field.create("Connection Status", status || "Not available"),
			Field.create("Active Connections", activeConnections || 0),
			Field.create("Protocol", protocol || "Not available"),
			Field.create("Last Active", lastOnline || "Not available"),
		]);
		return collapse.$container;
	},
	/**
	 * @param {ConnectionNode} connection
	 * @returns {JQuery<HTMLElement>}
	 */
	getSharingProfiles(connectionDump) {
		const { sharingProfiles } = connectionDump;
		const sharingCollapse = new Collapsible("Sharing Profiles");
		sharingCollapse.addHeaderIcon(fieldIcons.userGroup);
		if (!sharingProfiles || sharingProfiles.length === 0) {
			sharingCollapse.addContent(Field.create("Note", "No sharing profiles"));
			return sharingCollapse.$container;
		}
		sharingProfiles.forEach((profile) => {
			const collapse = new Collapsible(profile.name ?? "Unamed Profile");
			const profileInfo = detailsBuilder.initProfile(profile, collapse);
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
				Field.create("Note", "No profile data available")
			);
			return profileCollapse.$container;
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
		return profileCollapse.$container;
	},
};
