import { 
  Field, 
  Collapsible,
  TabData,
  TabContext,
  TabContent,
} from "../user-interface/node-modal.js/guac-modal.js";

/* features to add down the line  
  - Refresh Configuration 
    - Allow Multiple Refresh Attempts 
    - toggle refresh 
    - refresh speed options
  - Topology Preferences 
    - toggle inactive nodes
    Label Visibility 
      - hide leaf connection labels
        - all 
        - inactive 
      - hide connection group labels
      - hide root connection label 
    - icon preferences 
      - use default icons 
      - use connection counts
*/
export function settingsModalData(nodeContext, scheduler, settings) {
  if(!nodeContext) {
    throw new Error("No context was provided for the settings modal");
  }
  const modalTabData = [];
  const overviewContext = new TabContext("topOverview", "Topology Overview", "fa-solid fa-info");
  const overviewContent = buildOverviewTab(nodeContext, scheduler);
  modalTabData.push(new TabData(overviewContext, overviewContent));

  const settingsContext = new TabContext("topSettings", "Topology Settings", "fa-solid fa-gears");
  const settingsContent = new TabContent();
  settingsContent.addContent(initSettingControls(settings, scheduler));
  modalTabData.push(new TabData(settingsContext, settingsContent));
  return modalTabData;
}

function buildOverviewTab(nodeContext, { lastUpdated, upTime }) {
  const tabContent = new TabContent();
  const activeCount = nodeContext.countActiveConnections();
  const groupNodes = nodeContext.filterBy((node) => node.isGroup());
  
  let activeGroups = 0; 
  groupNodes.forEach((group) => {
    const childNodes = nodeContext.filterBy((node) => {
      return node.parentIdentifier === group.identifier
    });
    const activeCount = childNodes.filter((node) => node.isActive()).length || 0;
    activeGroups += (activeCount > 0) ? 1 : 0;
  });

  tabContent.addField(new Field("Total Connections", nodeContext.size));
  tabContent.addField(new Field("Active Connections", activeCount));
  tabContent.addField(new Field("Inactive Connections", nodeContext.size - activeCount));
  tabContent.addField(new Field("Total Connection Groups", groupNodes.length));
  tabContent.addField(new Field("Number of Active Connection Groups", activeCount));
  const $timeCollapsible = settingsTimeData(lastUpdated, upTime)
  tabContent.addContent($timeCollapsible);
  return tabContent;
}

function settingsTimeData(lastUpdated, upTime) {
  const uptimeCollapsible = new Collapsible("Time Information");
  const startField = new Field("Topology Start", new Date(upTime).toLocaleString());
  const lastUpdatedField = new Field("Last Updated", new Date(lastUpdated).toLocaleString());
  const uptimeField = new Field("Topology Uptime", new Date(upTime).toLocaleString());
  const refreshCountdown = new Field("Next Update", "00:00:00");
  const addFieldId = ($html, id) => {
    $html.find(".field-value").attr("id", id);
  };
  uptimeCollapsible.addContent([
    startField.toHTML(),
    lastUpdatedField.toHTML(),
    uptimeField.toHTML(null, null, "uptime-field"),
    refreshCountdown.toHTML(null, null, "refresh-countdown"),
  ]);
  return uptimeCollapsible.initalize();
}

function initSettingControls(settings, { stringDelay, delay }) {
  console.log(`refresh speed: ${delay}`);
  const determineStatus = (flag) => flag ? "active" : "inactive";
  const determineBtnIcon = (flag) => flag ? "fas fa-check" : "fas fa-times";
  const determineCheckboxIcon = (flag) => flag ? "fas fa-check-square" : "far fa-square";
  const { showInactive, refreshEnabled } = settings;
  // NOTE - maybe try using templates
  return $("<div>", {class: "settings-controls"}).html(`
    <div class="toggle-button ${determineStatus(showInactive)}" id="toggle-show-inactive">
      <i class="${determineBtnIcon(showInactive)}"></i>
      <span>Show Inactive Nodes</span>
    </div>

    <div class="toggle-button ${determineStatus(refreshEnabled)}" id="toggle-enable-refresh">
      <i class="${determineBtnIcon(refreshEnabled)}"></i>
      <span>Enable Refresh</span>
    </div>

    <div class="option-group refresh-speed">
      <div class="sub-option speed-option" data-speed="low">
        <i class="${determineCheckboxIcon(stringDelay === "low")}"></i>
        <span>Low <i>(30s)</i></span>
        <i class="fas fa-walking speed-icon"></i>
      </div>
      <div class="sub-option speed-option" data-speed="medium">
        <i class="${determineCheckboxIcon(stringDelay === "medium")}"></i>
        <span>Medium <i>(15s) [default]</i></span>
        <i class="fas fa-adjust speed-icon"></i>
      </div>
      <div class="sub-option speed-option" data-speed="high">
        <i class="${determineCheckboxIcon(stringDelay === "high")}"></i>
        <span>High <i>(5s)</i> </span> 
        <i class="fas fa-tachometer-alt speed-icon"></i>
      </div>
    </div>  
  `);
}











/* refresh speed options -v
<div class="refresh-speed">
  <div class="sub-option speed-option" data-speed="high">
    <i class="far fa-square"></i>
    <span>High</span>
    <i class="fas fa-tachometer-alt speed-icon"></i>
  </div>
  <div class="sub-option speed-option selected" data-speed="medium">
    <i class="fas fa-check-square"></i>
    <span>Medium</span>
    <i class="fas fa-adjust speed-icon"></i>
  </div>
  <div class="sub-option speed-option" data-speed="low">
    <i class="far fa-square"></i>
    <span>Low</span>
    <i class="fas fa-walking speed-icon"></i>
  </div>
</div>


*/







