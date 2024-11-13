import { 
  Field, 
  Collapsible,
  TabData,
  TabContext,
  TabContent,
} from "./guac-modal.js";


export function settingsModalData(nodeContext, scheduler, controller) {
  if(!nodeContext) {
    throw new Error("No context was provided for the settings modal");
  }
  const tabContext = new TabContext("settings", "Topology Settings", "fa-solid fa-gears");
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
  tabContent.addField(new Field("Last Updated", new Date(scheduler.lastUpdated).toLocaleString()));
  const controls = new Collapsible("Topology Controls");
  controls.addContent(initSettingControls(controller, scheduler.delay));
  tabContent.addContent(controls.initalize());
  return [new TabData(tabContext, tabContent)];
}

function initSettingControls(controller, refreshSpeed) {
  console.log(`refresh speed: ${refreshSpeed}`);
  const determineStatus = (flag) => flag ? "active" : "inactive";
  const determineBtnIcon = (flag) => flag ? "fas fa-check" : "fas fa-times";
  const determineCheckboxIcon = (flag) => flag ? "fas fa-check-square" : "far fa-square";

  const { showInactive, refreshEnabled } = controller;
  return $("<div>", {class: "settings-controls"}).html(`
    <div class="toggle-button ${determineStatus(showInactive)}" id="toggle-show-inactive">
      <i class="${determineBtnIcon(showInactive)}"></i>
      <span>Show Inactive Nodes</span>
    </div>

    <div class="toggle-button ${determineStatus(refreshEnabled)}" id="toggle-enable-refresh">
      <i class="${determineBtnIcon(refreshEnabled)}"></i>
      <span>Enable Refresh</span>
    </div>

    <div class="refresh-speed">
      <div class="speed-option" data-speed="high">
        <i class="far fa-square"></i>
        <span>High</span>
        <i class="fas fa-tachometer-alt speed-icon"></i>
      </div>
      <div class="speed-option" data-speed="medium">
        <i class="fas fa-check-square"></i>
        <span>Medium (default)</span>
        <i class="fas fa-adjust speed-icon"></i>
      </div>
      <div class="speed-option" data-speed="low">
        <i class="far fa-square"></i>
        <span>Low</span>
        <i class="fas fa-walking speed-icon"></i>
      </div>
    </div>  
  `);
}





/* refresh speed options -v
<div class="refresh-speed">
  <div class="speed-option" data-speed="high">
    <i class="far fa-square"></i>
    <span>High</span>
    <i class="fas fa-tachometer-alt speed-icon"></i>
  </div>
  <div class="speed-option selected" data-speed="medium">
    <i class="fas fa-check-square"></i>
    <span>Medium</span>
    <i class="fas fa-adjust speed-icon"></i>
  </div>
  <div class="speed-option" data-speed="low">
    <i class="far fa-square"></i>
    <span>Low</span>
    <i class="fas fa-walking speed-icon"></i>
  </div>
</div>


*/







