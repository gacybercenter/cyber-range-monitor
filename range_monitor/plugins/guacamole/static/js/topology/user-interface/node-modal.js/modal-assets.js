import { 
  ModalHTML,
  Field, 
  Collapsible,
  TabData,
  TabContext,
  TabContent,
} from "./guac-modal.js";
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
    const controlsTabData = TabInitiator.createNodeControls([connection], true);
    return [detailsTabData, controlsTabData];
  }
  /**
   * @param {ConnectionNode[]} selection
   * @returns {TabData[]}
   */
  static manyConnections(selection, nodeMap) {
    const generalTabData = TabInitiator.connectionOverview(selection, nodeMap);
    const controlsTabData = TabInitiator.createNodeControls(selection, true);
    return [generalTabData, controlsTabData];
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
    const overviewTabData = TabInitiator.groupOverviewTab(connGroup, childNodes, nodeMap);
    const statsTabData = TabInitiator.groupStatsData(childNodes);
    return [overviewTabData, statsTabData];
  }
}

class TabInitiator {
  static createNodeControls(selected, includeTimeline) {
    const identifiers = [];
    const tabContext = new TabContext("nodeControls", "Controls", "fa-solid fa-gears");
    const tabContent = new TabContent();
    selected.forEach((node) => identifiers.push(node.identifier));
    console.log(`Identifiers ${identifiers}`);
    console.log(`Typeof => ${typeof identifiers}`);
    tabContent.content = createNodeControls(identifiers, includeTimeline);
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
    const activeCount = childNodes.filter((node) => node.dump.activeConnections > 0).length ?? 0;
    
    stats.addField(new Field("Num. Child Connections", childNodes.length));
    stats.addField(new Field("Num. of Active Child Connections", activeCount));
    stats.addField(new Field("Status", activeCount > 0 ? "Online" : "Offline"));
    return new TabData(context, stats);
  }
}





/**
 *
 * @param {ConnectionNode} connGroup
 * @param {ConnectionNode[]} childNodes
 * @returns {Jquery<HTMLElement>[]}
 */
function groupStats(childNodes) {
  const stats = new TabContent();
  if (!childNodes) {
    stats.push(new Field("Note", "No child connections found").toHTML());
    return stats;
  }

  const activeCount =
    childNodes.filter((node) => node.dump.activeConnections > 0).length ?? 0;
  stats.push(
    new Field("Num. Child Connections", childNodes.length).toHTML(),
    new Field("Num. of Active Child Connections", activeCount).toHTML(),
    new Field("Status", activeCount > 0 ? "Online" : "Offline"),
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
      title: "Group Identifier",
      value: connGroup.identifier,
    }),
    ModalHTML.createField({
      title: "Group Type",
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
  if (!sharingProfiles && sharingProfiles.length >= 1) {
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