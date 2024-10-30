
// static/js/topology.js
import { Topology, TopologyController } from "./topology/display.js";


/**
 * @param {Topology} topology
 */
function setupControls(topology) {
  const refreshBtn = document.getElementById("refreshBtn");
  refreshBtn.addEventListener("click", () => {
    topology.toggleRefresh();
    toggleBtnAppearance(refreshBtn);
  });

  const inactiveBtn = document.getElementById("inactiveBtn");
  inactiveBtn.addEventListener("click", () => {
    topology.toggleInactive();
    toggleBtnAppearance(inactiveBtn);
  });

  const menuToggler = document.getElementById("menuToggler");
  menuToggler.addEventListener("click", () => {
    if (menuTag.classList.contains("active")) {
      restyle(menuTag, "active", "inactive");
      return;
    }
    restyle(menuTag, "inactive", "active");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const topology = new Topology();
  setupControls(topology);
  topology.render();
});
