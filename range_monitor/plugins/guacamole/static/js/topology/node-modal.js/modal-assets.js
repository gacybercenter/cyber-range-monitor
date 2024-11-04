import { Modal, ModalHTML } from "./guac-modal.js";

function parseSampleData() {
  const context = ContextHandler.getContext(SampleData.nodes);
  return context;
}

class ConnectionModal {
  /**
   * @param {ConnectionNode} connection
   * @returns {TabData[]}
   */
  static leafConnectionModal(connection, nodeMap) {
    const generalTabContent = generalTab(connection, nodeMap);
    const controlsTabContent = controlsTab();
    return [generalTabContent, controlsTabContent];
  }
  /**
   *
   * @param {ConnectionNode[]} connection
   * @returns {TabData[]}
   */
  static multiLeafModal(selectedConnections, nodeMap) {
    const generalTab = multiLeafGeneralTab(selectedConnections, nodeMap);
    const controls = controlsTab();
    console.log(generalTab);
    console.log(controls);
    return [generalTab, controls];
  }
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
 * @returns JQuery<HTMLElement>[]
 */
function initControlsHTML() {
  const makeControlBtn = (label, icon, cssClass) => {
    return $("<button>")
      .addClass("control-btn " + cssClass)
      .attr("aria-label", label).html(`
				<i class="icon fas ${icon}"></i>	
				${label}
			`);
  };
  return [
    makeControlBtn("Connect To", "fa-plug", "btn-connect"),
    makeControlBtn("Kill Connection", "fa-smile", "btn-kill"),
    makeControlBtn("View Timeline", "fa-chart-line", "btn-timeline"),
  ];
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

/**
 * @param {ConnectionNode[]} selectedConnections
 */
function multiLeafGeneralTab(selectedConnections, nodeMap) {
  const tabContext = {
    tabId: "multiLeafGeneral",
    title: "Connection Overview",
    fasIcon: "fa-solid fa-users-viewfinder",
  };
  const activeCount = selectedConnections.filter(
    (connection) => connection.dump.activeConnections > 0
  ).length;

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
    const title = connection.name ? connection.name : connection.identifier;
    const { $collapsible, $header, $content } =
      ModalHTML.createCollapsibleContainer(title);
    const nodeContent = generalTabContent(connection, nodeMap);
    nodeContent.forEach((field) => $content.append(field));
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
  const activeConnections = connection.dump.activeConnections;
  let status;
  if (!activeConnections || activeConnections < 0) {
    status = "Offline";
  } else {
    status = "Online";
  }
  const getLastActive = () => {
    if (connection.dump.lastActive) {
      const lastActive = new Date(connection.dump.lastActive);
      return lastActive.toUTCString();
    }
    return "Not available";
  };

  const connectionFields = [
    {
      title: "Active Connections",
      value: connection.dump.activeConnections || 0,
    },
    {
      title: "Connection Status",
      value: status || "Not available",
    },
    {
      title: "Protocol",
      value: connection.dump.protocol,
    },
    {
      title: "Last Active",
      value: getLastActive() || "Not available",
    },
  ];
  fields.push(ModalHTML.createCollapsible("Connectivity", connectionFields));
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

$(document).ready(() => {
  leaveExample();
  multiLeafModal();
});

/* 
    When a node is double clicked
    we want a modal to appear to 
    display information about said 
    node.

    -Tabs for Modal 

    Connection Leaf Node 
    -General
    
    Name: [Node Name]
    Identifier: [Node Identifier]
    Parent Connection: [Parent_Name]
    Parent Identifier: [Parent_Identifier]

    Connection Status
    Active Connections: [activeConnections]
    Last Active: [lastActive] ?? 
    Protocol: [protocol]


    Connection Properties [collapse]
    if empty
        -No attributes have been set for
        this connection     
    forEach(node.attribute)
        -Attribute Name: [attributeName]
     
    Sharing Profile [collapse]
    if not sharing profile 
    No attributes have been set for
        this connection
    forEach(node.sharingProfile)
        -Attribute Name: [attributeName]

    Tab 2 - Node Controls 
    Connect to Node 
    Refresh Node Data 
    Kill Connection
    View Timeline  

    Tab 3 - Node Connection Group Topology 
    - Do not show if multiple nodes are selected 
    
    - Show the connection group topology in the modal 
*/
