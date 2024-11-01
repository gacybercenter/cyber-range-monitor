
// static/js/topology.js
import { Topology, TopologyController } from "./topology/display.js";





const toggleBtnAppearance = (btn) => {
  const icon = btn.querySelector(".opt-icon");
  const wasOn = btn.classList.contains("on");

  if (wasOn) {
    btn.classList.replace("on", "off");
    icon.classList.replace("fa-check", "fa-times");
  } else if(btn.classList.contains("off")) {
    btn.classList.replace("off", "on");
    icon.classList.replace("fa-times", "fa-check");
  }
};

const setupNavHints = () => {
  const navHints = d3.select(".nav-hints");
  navHints.on("click", () => {
    navHints.classed("hidden", true);
  });
};


/**
 * sets up events for the menu to control
 * topology state 
 * @param {Topology} topology 
 */
function setupSettings(topology) {
  const refreshBtn = document.getElementById("refreshBtn");
  const inactiveBtn = document.getElementById("inactiveBtn");
  const menuTag = document.getElementById("settingsMenu");
  const menuToggler = document.getElementById("menuToggler");
  
  refreshBtn.addEventListener("click", () => {
    topology.toggleRefresh();
    toggleBtnAppearance(refreshBtn);
  });

  inactiveBtn.addEventListener("click", () => {
    topology.toggleInactive();
    toggleBtnAppearance(inactiveBtn);
  });
  
  menuToggler.addEventListener("click", () => {
    if (menuTag.classList.contains("active")) {
      menuTag.classList.replace("active", "inactive");
    } else {
      menuTag.classList.replace("inactive", "active");
    }
  });

}

document.addEventListener("DOMContentLoaded", () => {
  const topology = new Topology();
  setupSettings(topology);
  setupNavHints();
  topology.render();

});
