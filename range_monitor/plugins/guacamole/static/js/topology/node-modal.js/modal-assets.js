import { Modal, ModalHTML } from "./guac-modal.js";

export class ConnectionModals {
  /**
   * @param {ConnectionNode} connection
   * @returns {TabData[]}
   */
  static singleConnection(connection, nodeMap) {
    const generalTabContent = generalTab(connection, nodeMap);
    const controlsTabContent = controlsTab();
    return [generalTabContent, controlsTabContent];
  }
  /**
   *
   * @param {ConnectionNode[]} connection
   * @returns {TabData[]}
   */
  static manyConnection(selectedConnections, nodeMap) {
    const generalTab = multiLeafGeneralTab(selectedConnections, nodeMap);
    const controls = controlsTab();
    return [generalTab, controls];
  }
  /**
   *
   * @param {ConnectionNode} connGroup
   * @param {ConnectionNode[]} nodes
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData[]}
   */
  static connectionGroup(connGroup, nodes, nodeMap) {
    const childNodes = nodes.filter(
      (node) => node.parentIdentifier === connGroup.identifier
    );
    const overviewContext = {
      tabId: "groupOverview",
      title: "Group Overview",
      fasIcon: "fa-solid fa-users-viewfinder",
    };

    const overviewContent = groupOverviewTab(connGroup, childNodes, nodeMap);

    const statsContext = {
      tabId: "groupStats",
      title: "Connection Group Statistics",
      fasIcon: "fa-solid fa-chart-line",
    };

    const statsContent = connGroupStats(childNodes);

    return [
      {
        tabContext: overviewContext,
        tabContent: overviewContent,
      },
      {
        tabContext: statsContext,
        tabContent: statsContent,
      },
    ];
  }
}

/**
 *
 * @param {ConnectionNode} connGroup
 * @param {ConnectionNode[]} childNodes
 * @returns {Jquery<HTMLElement>[]}
 */
function connGroupStats(childNodes) {
  const stats = [];
  if (!childNodes) {
    stats.push(
      ModalHTML.createField({
        title: "Note",
        value: "No child connections found",
      })
    );
    return stats;
  }

  const activeCount =
    childNodes.filter((node) => node.dump.activeConnections > 0).length ?? 0;

  const isActive = activeCount > 0;

  stats.push(
    ModalHTML.createField({
      title: "Total Child Connections",
      value: childNodes.length,
    }),
    ModalHTML.createField({
      title: "Number of Active Connections",
      value: activeCount,
    }),
    ModalHTML.createField({
      title: "Status",
      value: isActive ? "Online" : "Offline",
    })
  );
  return stats;
}

function generalTab(connection, nodeMap) {
  const tabContext = {
    tabId: "nodeGeneral",
    title: "General",
    fasIcon: "fa-solid fa-circle-info",
  };
  const tabContent = generalTabContent(connection, nodeMap);
  return { tabContext, tabContent };
}

/**
 * Makes the timeline, connect & kill connection btns
 * for the modal.
 * @returns {JQuery<HTMLElement>[]}
 */
function initControlsHTML() {
  const initBtn = (label, icon, cssClass) => {
    return $("<button>")
      .addClass("control-btn " + cssClass)
      .attr("aria-label", label).html(`
				<i class="icon fas ${icon}"></i>	
				${label}
			`);
  };
  const connectBtn = initBtn("Connect To", "fa-plug", "btn-connect");
  const killBtn = initBtn("Kill Connection", "fa-smile", "btn-kill");

  killBtn.hover(
    function () {
      $(this).find("i").removeClass("fa-smile").addClass("fa-skull-crossbones");
    },
    function () {
      $(this).find("i").removeClass("fa-skull-crossbones").addClass("fa-smile");
    }
  );

  const timelineBtn = initBtn("View Timeline", "fa-chart-line", "btn-timeline");
  return [connectBtn, killBtn, timelineBtn];
}
function controlsTab() {
  const tabContext = {
    tabId: "nodeControls",
    title: "Controls",
    fasIcon: "fa-solid fa-gears",
  };
  const tabContent = initControlsHTML();
  return { tabContext, tabContent };
}

/* 
    activeConnections: 0,
    attributes: {
      "enable-session-affinity": "true",
      "max-connections": "100",
      "max-connections-per-user": "100",
    },
  identifier: "1851",
  name: "interns",
  parentIdentifier: "ROOT",
  type: "ORGANIZATIONAL",
*/

/**
 *
 * @param {ConnectionNode} connGroup
 * @param {ConnectionNode[]} nodes
 * @param {Map<string, ConnectionNode>} nodeMap
 * @returns
 */

function groupOverviewTab(connGroup, childNodes, nodeMap) {
  const fields = [
    ModalHTML.createField({
      title: "Connection Group Name",
      value: connGroup.name,
    }),
    ModalHTML.createField({
      title: "Connection Group Identifier",
      value: connGroup.identifier,
    }),
    ModalHTML.createField({
      title: "Connection Group Type",
      value: connGroup.dump.type ?? "Not set",
    }),
  ];
  // only null for root node, which is also a connection group
  if (connGroup.parentIdentifier) {
    const parent = nodeMap.get(connGroup.parentIdentifier);
    fields.push(
      ModalHTML.createField({
        title: "Parent Connection",
        value: parent.name,
      }),
      ModalHTML.createField({
        title: "Parent Identifier",
        value: parent.identifier,
      })
    );
  }

  const title = `${connGroup.name} Child Connections (${childNodes.length})`;
  const collapseObj = ModalHTML.createCollapsibleContainer(title);
  const { $collapsible, $header, $content } = collapseObj;
  childNodes.forEach((child) => {
    $content.append(
      ModalHTML.createField({
        title: "Child Connection Name",
        value: child.name,
      })
    );
  });
  $collapsible.append($header, $content);
  fields.push($collapsible);
  return fields;
}

/**
 * @param {ConnectionNode[]} selectedConnections
 */
function multiLeafGeneralTab(selectedConnections, nodeMap) {
  const tabContext = {
    tabId: "multiLeafGeneral",
    title: "Connection Overview",
    fasIcon: "fa-solid fa-users-viewfinder",
  };
  const active = selectedConnections.filter(
    (node) => node.dump.activeConnections > 0
  );
  const activeCount = active ? active.length : 0;
  const tabContent = [
    ModalHTML.createField({
      title: "Selected Connections",
      value: selectedConnections.length,
    }),
    ModalHTML.createField({
      title: "Selected Active Connections",
      value: activeCount,
    }),
  ];

  selectedConnections.forEach((connection) => {
    const fields = [
      ModalHTML.createField({
        title: "Connection Name",
        value: connection.name,
      }),
      ModalHTML.createField({
        title: "Node Identifier",
        value: connection.identifier,
      }),
      ModalHTML.createField({
        title: "Parent Connection",
        value: parent.name,
      }),
      ModalHTML.createField({
        title: "Parent Identifier",
        value: connection.parentIdentifier,
      }),
    ];
    const { $collapsible, $header, $content } =
      ModalHTML.createCollapsibleContainer(`${connection.name} Summary`);
    fields.forEach((field) => $content.append(field));
    $collapsible.append($header, $content);
    tabContent.push($collapsible);
  });
  return { tabContext, tabContent };
}

/**
 * @param {Map<string, ConnectionNode>} nodeMap
 * @param {ConnectionNode} connection
 */

function generalTabContent(connection, nodeMap) {
  const fields = [
    ModalHTML.createField({
      title: "Connection Name",
      value: connection.name,
    }),
    ModalHTML.createField({
      title: "Node Identifier",
      value: connection.identifier,
    }),
  ];
  let parent = nodeMap.get(connection.parentIdentifier);
  if (parent) {
    fields.push(
      ModalHTML.createField({
        title: "Parent Connection",
        value: parent.name,
      }),
      ModalHTML.createField({
        title: "Parent Identifier",
        value: connection.parentIdentifier,
      })
    );
  }
  const connectivity = getConnectivity(connection.dump);
  fields.push(connectivity);
  const attribute = connection.dump.attributes;
  const attrs = [];

  if (!attribute) {
    attrs.push({
      title: "Note",
      value: "No attributes have been set for this connection",
    });
  } else {
    Object.keys(attribute).forEach((key) => {
      attrs.push({
        title: key,
        value: attribute[key] ?? "Not set",
      });
    });
  }
  fields.push(ModalHTML.createCollapsible("Attributes", attrs));

  const sharing = [];
  const sharingProfiles = connection.dump.sharingProfiles;
  if (!sharingProfiles || sharingProfiles.length === 0) {
    sharing.push({
      title: "Note",
      value: "No sharing profiles have been set for this connection",
    });
  } else {
    sharingProfiles.forEach((profile) => {
      sharing.push(initProfile(profile));
    });
  }
  fields.push(ModalHTML.createCollapsible("Sharing Profile", sharing));
  return fields;
}

const getConnectivity = (connectionDump) => {
  const activeConnections = connectionDump.activeConnections;
  let status;
  if (!activeConnections || activeConnections < 0) {
    status = "Offline";
  } else {
    status = "Online";
  }

  const getLastActive = () => {
    if (connectionDump.lastActive) {
      const lastActive = new Date(connectionDump.lastActive);
      return lastActive.toUTCString();
    }
    return "Not available";
  };

  const connectionFields = [
    {
      title: "Active Connections",
      value: connectionDump.activeConnections || 0,
    },
    {
      title: "Connection Status",
      value: status || "Not available",
    },
    {
      title: "Protocol",
      value: connectionDump.protocol,
    },
    {
      title: "Last Active",
      value: getLastActive() || "Not available",
    },
  ];
  return ModalHTML.createCollapsible("Connectivity", connectionFields);
};

const initProfile = (profile) => {
  const profileData = [];
  Object.keys(profile).forEach((key) => {
    profileData.push({
      title: key,
      value: profile[key] ?? "Not set",
    });
  });
  if (profileData.length === 0) {
    profileData.push({
      title: "Note",
      value: "No attributes have been set for this connection",
    });
  }
  return profileData;
};

const getRandom = (arr) => {
  return arr[Math.floor(Math.random() * arr.length)];
};

function leaveExample() {
  const { nodes, nodeMap } = parseSampleData();
  console.log(nodeMap);
  const leaves = nodes.filter((node) => {
    return node.isLeafNode();
  });

  const modal = new Modal();
  $("#openGuacModal").on("click", () => {
    const randomLeaf = getRandom(leaves);
    const tabData = ConnectionModal.leafConnectionModal(randomLeaf, nodeMap);
    const title = randomLeaf.name || randomLeaf.identifier;
    modal.init(title, tabData);
    modal.openModal();
  });
}
function multiLeafModal() {
  const modal = new Modal();
  const { nodes, nodeMap } = parseSampleData();
  const leaves = nodes.filter((node) => {
    return node.isLeafNode();
  });
  const selection = [];

  for (let i = 0; i < 3; i++) {
    const selected = getRandom(leaves);
    selection.push(selected);
    console.log(`Selected Node -> ${selected.name}`);
  }

  const tabData = ConnectionModal.multiLeafModal(selection, nodeMap);
  $("#multiBtn").on("click", () => {
    modal.init("Connection Overview", tabData);
    modal.openModal();
  });
}

function groupModal() {
  const modal = new Modal();
  const { nodes, nodeMap } = parseSampleData();
  const groups = nodes.filter((node) => node.isGroup());
  const choice = getRandom(groups);

  const tabData = ConnectionModal.connectionGroupModal(choice, nodes, nodeMap);

  $("#groupBtn").on("click", function () {
    modal.init(choice.name, tabData);
    modal.openModal();
  });
}

