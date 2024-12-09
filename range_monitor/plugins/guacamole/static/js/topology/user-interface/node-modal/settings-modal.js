import { 
  Field, 
  Collapsible,
  ModalTab,
  COLLAPSE_STYLE,
} from "./components/modal-assets.js";

const modalIcons = {
  info: "fa-solid fa-info",
  settings: "fa-solid fa-gears",
  time: "fa-solid fa-clock-rotate-left",
};


export function settingsModalData(nodeContext, scheduler, settings) {
  if(!nodeContext) {
    throw new Error("No context was provided for the settings modal");
  }
  const overviewTab = new ModalTab("Topology Overview", modalIcons.info);
  settingsBuilder.buildOverviewTab(nodeContext, scheduler, overviewTab);
  const preferenceTab = new ModalTab("Preferences", modalIcons.settings);
  settingsBuilder.initSettingControls(settings, scheduler, preferenceTab);
  return [overviewTab, preferenceTab];
}


const settingsBuilder = {
  buildOverviewTab(nodeContext, { lastUpdated, upTime }, overviewTab) {
    const activeCount = nodeContext.countActiveConnections();
    const groupNodes = nodeContext.filterBy((node) => node.isGroup());
    
    let activeGroups = 0; 
    groupNodes.forEach(group => {
      const childNodes = nodeContext.filterBy((node) => {
        return node.parentIdentifier === group.identifier
      });
      const activeCount = childNodes
        .filter(node => node.isActive())
        .length || 0;
      activeGroups += +(activeCount > 0); // cast a bool to int, 999 iq 
    });
    overviewTab.addContent([
      Field.create("Total Connections", nodeContext.size),
      Field.create("Active Connections", activeCount),
      Field.create("Inactive Connections", nodeContext.size - activeCount),
      Field.create("Total Connection Groups", groupNodes.length),
      Field.create("Number of Active Connection Groups", activeCount),
    ]);

    const $timeCollapsible = this.settingsTimeData(lastUpdated, upTime)
    overviewTab.addContent($timeCollapsible);
  },

  settingsTimeData(lastUpdated, upTime) {
    const uptimeCollapsible = new Collapsible("Time Information", COLLAPSE_STYLE.FOLDER);
    uptimeCollapsible.addHeaderIcon(modalIcons.time);

    const upTimeString = new Date(upTime).toLocaleString();

    const startField = new Field("Topology Start", upTimeString);
    const uptimeField = new Field("Topology Uptime", upTimeString);
    const lastUpdatedField = new Field("Last Update", new Date(lastUpdated).toLocaleString());
    const refreshCountdown = new Field("Next Update", "00:00:00");
    uptimeCollapsible.addContent([
      startField.toHTML(),
      lastUpdatedField.toHTML(),
      uptimeField.toHTML({ valueId: "uptime-field" }),
      refreshCountdown.toHTML({valueId: "refresh-countdown"}),
    ]);
    return uptimeCollapsible.$container;
  },

  initSettingControls(settings, { stringDelay, delay }, preferenceTab) {
    console.log(`refresh speed: ${delay}`);
    const determineStatus = (flag) => flag ? "active" : "inactive";
    const determineBtnIcon = (flag) => flag ? "fas fa-check" : "fas fa-times";
    const determineCheckboxIcon = (flag) => flag ? "fas fa-check-square" : "far fa-square";
    const { showInactive, refreshEnabled } = settings;
    /* 
      NOTE to the next dev, try using templates for this
      i would myself but i'm already 3100 lines deep for the
      topology burnt out working on this feature
    */
    const $controls = $("<div>", {class: "settings-controls"}).html(`
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
    preferenceTab.addContent($controls);
  }
};
















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







