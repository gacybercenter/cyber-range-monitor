
// static/js/topology.js
import { Topology, TopologyController } from "./topology/display.js";


/**
 * @param {Topology} topology
 */
const restyle = (element, remove, add) => {
  element.classList.remove(remove);
  element.classList.add(add);
};


const toggleBtnAppearance = (btn) => {
  const icon = btn.querySelector(".opt-icon");
  if (btn.classList.contains("on")) {
    restyle(btn, "on", "off");
    restyle(icon, "fa-check", "fa-times");
    return;
  }
  
  restyle(btn, "off", "on");
};

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
  const menuTag = document.getElementById("settingsMenu");
  const menuToggler = document.getElementById("menuToggler");
  menuToggler.addEventListener("click", () => {
    if (menuTag.classList.contains("active")) {
      restyle(menuTag, "active", "inactive");
    } else {
      restyle(menuTag, "inactive", "active");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const topology = new Topology();
  setupControls(topology);
  topology.render();
});
