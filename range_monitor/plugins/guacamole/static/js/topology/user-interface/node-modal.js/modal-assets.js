import { ConnectionNode } from "../../data/guac_types.js";
import { 
  Field, 
  Collapsible,
  TabData,
  TabContext,
  TabContent,
} from "./guac-modal.js";
import { renderGroupSelector } from "./group-select.js";
import { createNodeControls } from "./node-btns.js";
export { ConnectionModals };

/* 
  NOTE / TODO
  try to use classes instead of objects (in guac-modal.js)
  to reduce lines of code and improve readability
*/
class ConnectionModals {
  /**
   * @param {ConnectionNode} connection
   * @returns {TabData[]}
   */
  static singleConnection(connection, nodeMap) {
    const detailsTabData = TabInitiator.singleNodeDetails(connection, nodeMap);
    const controlsTabData = TabInitiator.createNodeControls([connection.identifier], true);
    return [detailsTabData, controlsTabData];
  }

  /**
   * @param {ConnectionNode[]} selection
   * @returns {TabData[]}
   */
  static manyConnections(selection, nodeMap) {
    const selectedNodes = selection.map((ids) => nodeMap.get(ids));
    const generalTabData = TabInitiator.connectionOverview(selectedNodes, nodeMap);
    const controlsTabData = TabInitiator.createNodeControls(selectedNodes, true);
    return [generalTabData, controlsTabData];
  }
  /**
   *
   * @param {ConnectionNode} connGroup
   * @param {ConnectionNode[]} nodes
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData[]}
   */
  static connectionGroup(connGroup, nodes, nodeMap, userSelection) {
    const childNodes = nodes.filter(
      (node) => node.parentIdentifier === connGroup.identifier
    );
    userSelection.length = 0;
    const overviewTabData = TabInitiator.groupOverviewTab(connGroup, childNodes, nodeMap);
    const statsTabData = TabInitiator.groupStatsData(childNodes);
    const controlsTabData = groupControlsTab(childNodes, userSelection);
    return [overviewTabData, statsTabData, controlsTabData];
  }
}

class TabInitiator {
  static createNodeControls(selected, includeTimeline) {
    const tabContext = new TabContext("nodeControls", "Controls", "fa-solid fa-gears");
    const tabContent = new TabContent();
    tabContent.content = createNodeControls(selected, includeTimeline);
    return new TabData(tabContext, tabContent);
  }
  /**
   * @param {ConnectionNode} connection
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData}
   */
  static singleNodeDetails(connection, nodeMap) {
    const tabContent = generalTabContent(connection, nodeMap);
    const tabContext = new TabContext("nodeDetails", "Details", "fa-solid fa-circle-info");
    return new TabData(tabContext, tabContent);
  }
  /**
   * @param {ConnectionNode[]} selection
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData}
   */
  static connectionOverview(selection, nodeMap) {
    const tabContext = new TabContext("connectionOverview", "Connection Overview", "fa-solid fa-users-viewfinder");
    const activeNodes = selection.filter(
      (node) => node.dump.activeConnections > 0
    );
    let activeCount = 0;
    if(activeNodes) {
      activeCount = activeNodes.length;
    }
    const tabContent = new TabContent();
    tabContent.addField(new Field("Num. Selected Connections", selection.length));
    tabContent.addField(new Field("Num. Active Connections", activeCount));

    const childCollapsible = new Collapsible("Child Connection Summary");
    selection.forEach((connection) => {
      const fields = [
        new Field("Connection Name", connection.name),
      ];
      let parent = nodeMap.get(connection.parentIdentifier);
      if(parent) {
        fields.push(new Field("Parent Connection", parent.name));
      }
      childCollapsible.addContent(Collapsible.createGeneric(connection.name, fields))
    });
    tabContent.addContent(childCollapsible.initalize());
    return new TabData(tabContext, tabContent);
  }
  /**
   * @param {ConnectionNode} connGroup
   * @param {ConnectionNode[]} childNodes
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData}
   */
  static groupOverviewTab(connGroup, childNodes, nodeMap) {
    const tabContext = new TabContext("groupOverview", "Group Overview", "fa-solid fa-users-viewfinder");
    const tabContent = new TabContent();

    tabContent.addField(new Field("Connection Group Name", connGroup.name));
    tabContent.addField(new Field("Group Identifier", connGroup.identifier));
    tabContent.addField(new Field("Group Type", connGroup.dump.type ?? "Not set"));

    if (connGroup.parentIdentifier) {
      const parent = nodeMap.get(connGroup.parentIdentifier);
      tabContent.addField(new Field("Parent Connection", parent.name));
      tabContent.addField(new Field("Parent Identifier", parent.identifier));
    }

    const title = `Child Connection Summary (${childNodes.length})`;
    const childSummary = new Collapsible(title);
    childNodes.forEach((child) => {
      childSummary.addField(new Field(child.name, `[${child.identifier}]`));
    });
    tabContent.addContent(childSummary.initalize());
    return new TabData(tabContext, tabContent);
  }
  static groupStatsData(childNodes) {
    const context =  new TabContext("groupStats", "Connection Group Statistics", "fa-solid fa-chart-line");
    const stats = new TabContent();
    if (!childNodes) {
      stats.addField(new Field("Note", "No child connections found"));
      return stats;
    }
    const activeCount = childNodes.filter((node) => {
      return node.dump.activeConnections > 0
    }).length ?? 0;
    
    stats.addField(new Field("Num. Child Connections", childNodes.length));
    stats.addField(new Field("Num. of Active Child Connections", activeCount));
    stats.addField(new Field("Status", activeCount > 0 ? "Online" : "Offline"));
    return new TabData(context, stats);
  }
}

function groupControlsTab(childConnections, userSelection) {
  const tabContext = new TabContext(
    "groupControls", "Controls", "fa-solid fa-gears"
  ); 
  const tabContent = new TabContent();
  const $groupSelector = renderGroupSelector(childConnections, userSelection);
  tabContent.addContent($groupSelector);
  const controlsCollapsible = new Collapsible("Controls");  
  const controlBtns = createNodeControls(userSelection, false);
  controlsCollapsible.addContent(controlBtns);
  

  tabContent.addContent(controlsCollapsible.initalize());
  return new TabData(tabContext, tabContent);
}

function generalTabContent(connection, nodeMap) {
  const tabContent = new TabContent();
  tabContent.addField(new Field("Connection Name", connection.name));
  tabContent.addField(new Field("Node Identifier", connection.identifier));
  
  let parent = nodeMap.get(connection.parentIdentifier);
  
  if (parent) {
    tabContent.addField(new Field("Parent Connection", parent.name));
    tabContent.addField(new Field("Parent Identifier", parent.identifier));
  }
  
  const $details = getDetails(connection);
  tabContent.addContent($details);
  return tabContent;
}

const getDetails = function(connection) {
  const details = new Collapsible("Detailed Overview");
  
  const attributes  = getAttributes(connection);
  details.addContent(attributes);

  const connectivity = getConnectivity("Connectivity", getConnectivity(connection.dump));
  details.addContent(connectivity);
  
  const sharing = getSharingProfiles(connection);
  details.addContent(sharing);
  return details.initalize();
}
function getAttributes(connection) {
  const attribute = connection.dump.attributes;
  const attrFields = [];
  if (!attribute) {
    attrFields.push(new Field("Note", "No attributes have been set for this connection"));
  } else {
    Object.keys(attribute).forEach((key) => {
      attrFields.push(new Field(key, attribute[key] ?? "Not set"));
    });
  }
  return Collapsible.createGeneric("Attributes", attrFields)
}

/**
 * @param {*} connectionDump 
 * @param {TabContent} tabContent 
 * @returns {JQuery<HTMLElement>}
 */
const getConnectivity = (connectionDump) => {
  const activeConnections = connectionDump.activeConnections;
  let status = "Online";
  if (!activeConnections || activeConnections < 0) {
    status = "Offline";
  } 
  const getLastActive = () => {
    if (connectionDump.lastActive) {
      const lastActive = new Date(connectionDump.lastActive);
      return lastActive.toUTCString();
    }
    return "Not available";
  };
  const connectionFields = [
    new Field("Connection Status", status || "Not available"),
    new Field("Num. Active Connections", activeConnections || 0),
    new Field("Protocol", connectionDump.protocol || "Not available"),
    new Field("Last Active", getLastActive() || "Not available"),
  ];
  return Collapsible.createGeneric("Connectivity Properties", connectionFields);
};

const getSharingProfiles = (connection) => {
  const sharing = [
    new Field("Note", "No sharing profiles have been set for this connection").toHTML(),
  ];
  const sharingProfiles = connection.dump.sharingProfiles;
  if (sharingProfiles && sharingProfiles.length >= 1) {
    sharing.pop();
    sharingProfiles.forEach((profile) => {
      sharing.push(initProfile(profile));
    });
  }
  return sharing;
}

const initProfile = (profile) => {
  const profileData = [];
  
  if (profileData.length === 0) {
    profileData.push(new Field("Note", "No profile data available"));
    return profileData;
  }

  Object.keys(profile).forEach((key) => {
    profileData.push(new Field(key, profile[key]).toHTML());
  });
  return profileData;
};





