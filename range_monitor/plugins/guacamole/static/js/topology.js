// static/js/topology.js
import { Topology } from "./topology/topology_ui.js";
import {
  NavigationHints,
  StatusUI,
} from "./topology/user-interface/ui_hints.js";

function toggleBtnAppearance($btn) {
  if($btn.length === 0) {
    console.log("A topology control button was not found");
    return;
  }
  const $icon = $btn.find(".opt-icon");

  if ($btn.hasClass("on")) {
    $btn.removeClass("on").addClass("off");
    $icon.removeClass("fa-check").addClass("fa-times");
  } else if ($btn.hasClass("off")) {
    $btn.removeClass("off").addClas;
    s("on");
    $icon.removeClass("fa-times").addClass("fa-check");
  }
}

/**
 * sets up events for the menu to control
 * topology state
 * @param {Topology} topology
 */
function setupSettings(topology) {
  $("#refreshBtn").on("click", function () {
    topology.toggleRefresh();
    toggleBtnAppearance($(this));
  });

  $("#inactiveBtn").on("click", function () {
    topology.toggleInactive();
    toggleBtnAppearance($(this));
  });

  $("#menuToggler").on("click", function () {
    $("#settingsMenu").toggleClass("active inactive");
  });
}

async function tryLoadTopology(statusUI) {
  const topology = new Topology();
  setupSettings(topology);
  NavigationHints.init();
  await topology.render()
    .catch(error => {
      handleError(error, statusUI);
    });
  return topology;
}

/**
 *
 * @param {string} err
 * @param {StatusUI} status
 */
function handleError(error, status) {
  const $retryBtn = status.toErrorMessage(error);
  $retryBtn.on("click", function () {
    status.toLoading();
    tryToRender(status);
  });
}

/**
 * 
 * @param {StatusUI} status 
 */
function tryToRender(status = null) {
  if(!status) {
    status = new StatusUI();
    status.loading();
  } else {
    status.toLoading();
  }
  initialLoad()
    .then(() => {
      clearInterval(status.loadInterval);
      status.hide();
    })
    .catch((err) => {
      handleError(err, status);
    });
}

$(function () {
  loadTopology
});
