import { ConnectionNode } from "../../data/guac_types.js";
import { 
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

/* 
  the plan

  create a modal for controlling the topology settings 
  

  Regenerate / Refresh 
  
  Update Frequency [
    Low (45s)
    Medium (30s)
    High (15s)
  ]

  Last Updated [timestamp]
  Topology Uptime [timestamp]
  Data Source [URL]

  Total Connections: [number]
  Active Connections: [number]
  
  Inactive Connections: [number]
  Total Groups: [number]

  Topology Preferences 
  [x] Display Inactive Connections / Nodes 
  [x] Enabled Refresh 


*/


function groupControlsTab(childConnections, userSelection) {
  const tabContext = new TabContext(
    "groupControls", "Controls", "fa-solid fa-gears"
  ); 
  const tabContent = new TabContent();
  const controlsCollapsible = new Collapsible("Controls");
  const controlBtns = createNodeControls(childConnections, false);
  controlsCollapsible.addContent(controlBtns);
  initSelectionCheckboxes(tabContent, childConnections, userSelection);
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

/**
 * @param {Collapsible} collapsible 
 * @param {ConnectionNode[]} childConnections 
 * @param {Map<string, ConnectionNode>} nodeMap 
 */
const initSelectionCheckboxes = (tabContent, childConnections, userSelection) => {
  const $panel = createControlPanel(childConnections);
  tabContent.addContent($panel);

  const $checkboxGroup = $("<div>", { class: "checkbox-group" });
  const selectAllBox = `
    <div class="checkbox-item select-all" id="select-all">
      <i class="fa-regular fa-rectangle-xmark icon icon-deselected"></i>
      <label>Select All</label>
    </div>
  `;
  $checkboxGroup.append(selectAllBox);

  createCheckboxes($checkboxGroup, childConnections);

  const childIds = childConnections.map((node) => node.identifier);
  const components = {
    filterBtns: $panel.find(".filter-btn"),
    selectedCount: $panel.find("#selected-count"),
    selectAll: $checkboxGroup.find("#select-all"),
    checkboxes: $checkboxGroup.find(".checkbox-option"),
  };

  addCheckBoxEvents(userSelection, components, childIds);
  tabContent.addContent($checkboxGroup);
};

function addCheckBoxEvents(userSelection, components, childIds) {
  const { filterBtns, selectedCount, selectAll, checkboxes } = components;

  const toggleIcon = ($icon, isSelected) => {
    $icon.stop(true, true).fadeOut(150, function () {
      if (isSelected) {
        $icon
          .removeClass("fa-rectangle-xmark icon-deselected")
          .addClass("fa-square-check icon-selected");
      } else {
        $icon
          .removeClass("fa-square-check icon-selected")
          .addClass("fa-rectangle-xmark icon-deselected");
      }
      $icon.fadeIn(150);
    });
  };

  let currentFilter = null;
  const filterConnections = (filter) => {
    checkboxes.removeClass("hidden");
    if (filter === 'all') {
      currentFilter = null;
      return;
    }
    if (filter === "active") {
      currentFilter = '[data-active="true"]';
    } else {
      currentFilter = '[data-active="false"]';
    }
    checkboxes.not(currentFilter).addClass("hidden");
  };

  const debugInfo = () => {
    console.log("Current Filter: ", currentFilter);
    console.log("Selected IDs: ", userSelection);
    console.log("Child IDs: ", childIds);
  };

  const updateSelectAll = () => {
    const $selectIcon = selectAll.find(".icon");
    const selected = selectAll.hasClass("selected");
    const visibleItems = checkboxes.filter(':visible').length;
    const selectedVisible = checkboxes.filter('.selected:visible').length;

    const allVisibleSelected = (visibleItems > 0 && 
      selectedVisible === visibleItems
    );

    if (allVisibleSelected && !selected) {
      selectAll.addClass("selected");
      toggleIcon($selectIcon, true);
    } else if (!allVisibleSelected && selected) {
      selectAll.removeClass("selected");
      toggleIcon($selectIcon, false);
    }
  };

  const rebuildSelection = () => {
    userSelection.length = 0;
    checkboxes.filter(".selected").each(function () {
      userSelection.push(`${$(this).data("node-id")}`);
    });
  };

  checkboxes.click(function () {
    const $icon = $(this).find(".icon");
    const wasSelected = $icon.hasClass("icon-selected");
    $(this).toggleClass("selected");
    toggleIcon($icon, !wasSelected);
    rebuildSelection();
    updateSelectAll();
    selectedCount.text(userSelection.length);
    debugInfo();
  });

  selectAll.click(function () {
    const wasSelected = $(this).hasClass("selected");
    $(this).toggleClass("selected");
    toggleIcon($(this).find(".icon"), !wasSelected);
    const selection = checkboxes.filter(':visible');
    if (wasSelected) {
      selection.removeClass("selected");
    } else {
      selection.addClass("selected");
    }
    selection.each(function () {
      const $icon = $(this).find(".icon");
      toggleIcon($icon, !wasSelected);
    });

    rebuildSelection();
    updateSelectAll();
    selectedCount.text(userSelection.length);
    debugInfo();
  });

  filterBtns.click(function () {
    filterBtns.removeClass("active");
    $(this).addClass("active");
    filterConnections($(this).data("filter"));
    updateSelectAll();
  });
}

const createCheckboxes = ($checkboxGroup, childConnections) => {
  childConnections.forEach((connection) => {
    const checkbox = `
      <div class="checkbox-item checkbox-option" 
        data-node-id="${connection.identifier}" 
        data-active="${connection.isActive()}"
      >
        <i class="fa-regular fa-rectangle-xmark icon icon-deselected"></i>
        <label class="checkbox-label">
          ${connection.name} ${connection.getOsIcon()}
        </label>
      </div>
    `;
    $checkboxGroup.append(checkbox);
  });
};

const createControlPanel = (childNodes) => {
  const activeCount = childNodes.filter((node) => node.isActive()).length || 0;
  const inactiveCount = childNodes.length - activeCount;
  const $controlPanel = $("<div>", { class: "control-panel" }).html(`
    <div class="control-panel">
      <div class="counter">Selected: <span id="selected-count">0</span></div>
      <div class="filters">
        <button class="filter-btn active" data-filter="all">
          All (${childNodes.length}) <i class="fa-solid fa-users-rectangle"></i>
        </button>
        <button class="filter-btn" data-filter="active">
          Active (${activeCount}) <i class="fa-regular fa-eye"></i>
        </button>
        <button class="filter-btn" data-filter="inactive">
          Inactive (${inactiveCount}) <i class="fa-regular fa-eye-slash"></i>
        </button>
      </div>
    </div>
  `);
  return $controlPanel;
};













