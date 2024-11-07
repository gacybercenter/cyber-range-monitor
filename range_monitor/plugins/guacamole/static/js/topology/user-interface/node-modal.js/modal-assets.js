import { ModalHTML } from "./guac-modal.js";
import { createNodeControls } from "./node-btns.js";
export { ConnectionModals };

/* 
  NOTE / TODO
  try to use classes instead of objects (in guac-modal.js)
  to reduce lines of code and improve readability
*/
export class ConnectionModals {
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
    const statsTabData = TabInitiator.groupStatsContent(childNodes);
    return [overviewTabData, statsTabData];
  }
}

class TabInitiator {
  static createNodeControls(selected, includeTimeline) {
    const identifiers = [];
    selected.forEach((node) => identifiers.push(node.identifier));
    console.log(`Identifiers ${identifiers}`);
    console.log(`Typeof => ${typeof identifiers}`);
    const buttonsHTML = createNodeControls(identifiers, includeTimeline);
    return {
      tabContext: {
        tabId: "nodeControls",
        title: `Controls (${selected.length})`,
        fasIcon: "fa-solid fa-gears",
      },
      tabContent: buttonsHTML,
    };
  }
  /**
   * @param {ConnectionNode} connection
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData}
   */
  static singleNodeDetails(connection, nodeMap) {
    const tabHTML = generalTabContent(connection, nodeMap);
    return {
      tabContext: {
        tabId: "nodeDetails",
        title: "Details",
        fasIcon: "fa-solid fa-circle-info",
      },
      tabContent: tabHTML,
    };
  }
  /**
   * @param {ConnectionNode[]} selection
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData}
   */
  static connectionOverview(selection, nodeMap) {
    const tabContext = {
      tabId: "connectionOverview",
      title: `Connection Overview (${selection.length})`,
      fasIcon: "fa-solid fa-users-viewfinder",
    };
    const activeNodes = selection.filter(
      (node) => node.dump.activeConnections > 0
    );
    let activeCount = 0;
    if(activeNodes) {
      activeCount = activeNodes.length;
    }
    const tabContent = [
      ModalHTML.createField({
        title: "Selected Connections",
        value: selection.length,
      }),
      ModalHTML.createField({
        title: "Selected Active Connections",
        value: activeCount,
      }),
    ];

    selection.forEach((connection) => {
      let parent = nodeMap.get(connection.parentIdentifier);
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
          value: parent ? parent.name : "None",
        }),
        ModalHTML.createField({
          title: "Parent Identifier",
          value: parent ? parent.identifier : "None",
        }),
      ];
      const { $collapsible, $header, $content } =
        ModalHTML.createCollapsibleContainer(`${connection.name} Summary`);
      fields.forEach(
        (field) => $content.append(field)
      );
      $collapsible.append($header, $content);
      tabContent.push($collapsible);
    });

    return { tabContext, tabContent };
  }
  /**
   * @param {ConnectionNode} connGroup
   * @param {ConnectionNode[]} childNodes
   * @param {Map<string, ConnectionNode>} nodeMap
   * @returns {TabData}
   */
  static groupOverviewTab(connGroup, childNodes, nodeMap) {
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
    return {
      tabContext: {
        tabId: "groupOverview",
        title: "Group Overview",
        fasIcon: "fa-solid fa-users-viewfinder",
      },
      tabContent: fields,
    };
  }
  static groupStatsContent(childNodes) {
    const context = {
      tabId: "groupStats",
      title: "Connection Group Statistics",
      fasIcon: "fa-solid fa-chart-line",
    };
    const stats = [];

    if (!childNodes) {
      stats.push(
        ModalHTML.createField({
          title: "Note",
          value: "No child connections found",
        })
      );
      return {
        tabContext: context,
        tabContent: stats,
      };
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
    return {
      tabContext: context,
      tabContent: stats
    };
  }
}





/**
 *
 * @param {ConnectionNode} connGroup
 * @param {ConnectionNode[]} childNodes
 * @returns {Jquery<HTMLElement>[]}
 */
function groupStats(childNodes) {
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