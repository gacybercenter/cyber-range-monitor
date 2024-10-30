
// static/js/topology.js
import { GuacNode, ConnectionGroup, GuacContext } from "./topology/api_data.js";
import { TopologySetup, GraphAssets } from "./topology/ui_setup.js";

class TopologyError extends Error {
  constructor(message) {
    super(
      `TopologyError: something went wrong in the topology.\n[INFO] - ${message}`
    );
    this.name = "TopologyError";
  }
}

const safeGetById = (id) => {
  const tag = document.getElementById(id);
  if (!tag) {
    throw new TopologyError(`Element with id ${id} not found`);
  }
  return tag;
};



const xhrRequestTo = (endpoint) => {
  const apiEndpoint = `/guacamole/api/${endpoint}`;
  const xhrGuac = new XMLHttpRequest();
  xhrGuac.open("POST", apiEndpoint, true);
  xhrGuac.setRequestHeader("Content-Type", "application/json");
  return xhrGuac;
};


// IGNORE THIS CODE 
// class ButtonHandler {
//   static connectBtn() {
//     const xhr = xhrRequestTo("connect-connections");
//     xhr.onreadystatechange = function () {
//       if (xhr.readyState !== XMLHttpRequest.DONE) {
//         return;
//       }
//       // when ready but not 200
//       if (xhr.status !== 200) {
//         alert(xhr.responseText);
//         return;
//       }
//       var response = JSON.parse(xhr.responseText);
//       var url = response.url;
//       var token = response.token;
//       var link = `${url}?token=${token}`;
//       window.open(link, "_blank");
//       console.log(response);
//     };
//     var data = JSON.stringify({ identifiers: selectedIdentifiers });
//     xhr.send(data);
//   }
//   static killBtn() {
//     const xhr = xhrRequestTo("kill-connections");
//     xhr.onreadystatechange = function () {
//       if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
//         const response = JSON.parse(xhr.responseText);
//         console.log(response);
//       } else if (xhr.readyState === XMLHttpRequest.DONE) {
//         alert(xhr.responseText);
//       }
//     };
//     const data = JSON.stringify({ identifiers: selectedIdentifiers });
//     xhr.send(data);
//   }
//   static timelineBtn() {
//     window.open(selectedIdentifiers[0] + "/connection_timeline", "_blank");
//   }
// }
// class NodeControls {
//   constructor() {
//     this.connectBtn = safeGetById("connect-button");
//     this.killBtn = safeGetById("kill-button");
//     this.timelineBtn = safeGetById("timeline-button");
//   }
//   /**
//    * adds the event listeners to the btns
//    * logic for each btn is in ButtonHandler
//    */
//   addEvents() {
//     this.connectBtn.addEventListener("click", () => {
//       if (!haveIdentifiers()) {
//         return;
//       }
//       ButtonHandler.connectBtn();
//     });

//     this.killBtn.addEventListener("click", () => {
//       if (!haveIdentifiers()) {
//         return;
//       }
//       ButtonHandler.killBtn();
//     });

//     this.timelineBtn.addEventListener("click", () => {
//       if (!haveIdentifiers()) {
//         return;
//       }
//       ButtonHandler.timelineBtn();
//     });
//   }
// }


/**
 * @class TopologyControls
 * @description responsible for controlling whats shown on the topology
 * @property {HTMLElement} refreshBtn - the refresh button
 * @property {HTMLElement} inactiveBtn - the inactive button
 */
const fetchGuacData = async () => {
  const guacEndpoint = "api/topology_data";
  const response = await fetch(guacEndpoint);
  if (!response.ok) {
    throw new TopologyError("Failed to retrieve Guac data.");
  }
  const jsonData = await response.json();
  return jsonData;
};

class TopologyController {
  constructor() {
    this.refreshEnabled = true;
    this.showInactive = true;
    this.selectedIdentifiers = [];
    this.updateInterval = null;
  }
  resetInterval() {
    if(this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }
  setInterval(callback, ms) {
    this.updateInterval = setInterval(callback, ms);
  }

  async getGuacNodes() {
    try {
      const guacDump = await fetchGuacData();
      return guacDump.nodes;
    } catch (err) {
      console.error(`GUAC_ERROR: Could not fetch nodes; ${err}`);
      return null;
    }
  }
  /**
   * filters out nodes based on "showInactive"
   * prop
   * @param {Object[]} nodes 
   * @returns 
   */
  filterNodesByStatus(nodes) {
    const nodeIsActive = (node) => {
      return node.identifier && node.activeConnections > 0;
    };

    if (this.showInactive) {
      return nodes.filter((node) => node.identifier);
    } else {
      return nodes.filter(nodeIsActive);
    }
  }
}

const setupDrag = () => {
  function dragStarted(event, d) {
    if (!event.active) {
      simulation.alphaTarget(0.1).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
    // if (updateId) {
    //   clearInterval(updateId);
    //   // ???
    // }
  }
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  function dragEnded(event, d) {
    if (!event.active) {
      simulation.alphaTarget(0);
    }
    d.fx = null;
    d.fy = null;
    // maybe ???
    // if (TopologyStatus.refreshEnabled) {
    //   updateId = setInterval(updateTopology, 5000);
    // }
  }
  return d3
    .drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded);
};

/**
 * @class Topology
 * @description Represents the topology of the network, including the SVG elements, simulation, and data handling.
 * @property {Object} svg - The SVG element used for rendering the topology.
 * @property {Object} container - The container element for the SVG.
 * @property {Object} simulation - The D3 simulation object used for force-directed layout.
 * @property {GraphAssets} assets - The assets used for rendering nodes and edges in the topology.
 * @property {TopologyController} controller - The controller responsible for managing topology data and state.
 * @property {GuacContext|null} context - The context containing the current state of nodes and links.
 * @property {Map|null} positions - A map of node positions keyed by node identifier.
 */
class Topology {
  constructor() {
    const { svg, container } = TopologySetup.initSVG();
    this.svg = svg;
    this.container = container;
    TopologySetup.setupZoom(svg, container);
    this.simulation = TopologySetup.setupSimulation(svg);
    this.drag = setupDrag();
    this.assets = new GraphAssets(svg);
    this.controller = new TopologyController();
    this.context = null;
    this.positions = null;
  }
  getPositions() {
    return new Map(
      this.assets.node.data().map((d) => {
        [d.positionKey, { x: d.x, y: d.y }];
      })
    );
  }
  async render() {
    const data = await this.controller.getGuacNodes();
    if (!data) {
      console.warn("No data was returned by API");
      return;
    }
    
    const nodes = data.nodes;

    if(!nodes) {
      console.warn("No nodes were returned by the api (huh)");
      return;
    }
    
    const filteredNodes = this.controller.filterNodesByStatus(nodes);
    
    let alphaValue;
    if (!this.context) {
      console.log("initializing context");
      alphaValue = 1;
      this.context = new GuacContext();
      this.initializeUI(alphaValue, filteredNodes);
    } else {
      const contextChanged = this.context.updateNodes(filteredNodes);
      if (contextChanged) {
        alphaValue = 0.1;
        this.initializeUI(alphaValue, filteredNodes);
      }
    }
  }

  /**
   * @param {number} alphaValue - the force to apply to the nodes
   * @param {Object[]} filteredNodes - inactive or active nodes
   */
  initializeUI(alphaValue, filteredNodes) {
    this.context.buildContext(filteredNodes);
    
    this.assets.setEdges(this.context.links);
    this.assets.setNodes(this.context.guacNodes, this);
    this.assets.setLabels(this.context.guacNodes);

    this.simulation.nodes(this.context.guacNodes);
    this.simulation.force("link").links(this.context.edges);
    this.simulation.alpha(alphaValue).restart();

    this.onSimulationTick();
    console.log("context built");
  }
  onSimulationTick() {
    this.simulation.on("tick", () => {
      this.assets.edge
        .attr("x1", (d) => d.source.x)
        .attr("x2", (d) => d.target.x)
        .attr("y1", (d) => d.source.y)
        .attr("y2", (d) => d.target.y);
      this.assets.node
          .attr("cx", (d) => d.x)
          .attr("cy", (d) => d.y);
      this.assets.label
          .attr("x", (d) => d.x)
          .attr("y", (d) => d.y);
    });
  }
  toggleRefresh() {
    this.controller.refreshEnabled = !this.controller.refreshEnabled;
    if (this.controller.refreshEnabled) {
      this.render();
      this.controller.setInterval( () => {
        this.render();
      }, 5000);
    } else {
      this.controller.resetInterval();
    }
  }
  toggleInactive() {
    this.controller.showInactive = !this.controller.showInactive;
    this.render();
    this.svg.selectAll("circle").classed("selected", false);
    selectedIdentifiers = null;
    if (this.controller.refreshEnabled) {
      this.controller.setInterval(this.render, 5000);
    }
  }
}

const restyle = (tag, oldStyle, newStyle) => {
  tag.classList.replace(oldStyle, newStyle);
};
  
const toggleBtnAppearance = (btn) => {
  const icon = btn.querySelector(".opt-icon");
  
  if (btn.classList.contains("on")) {
    restyle(btn, "on", "off");
    restyle(icon, "fa-check", "fa-times");
    return;
  }

  restyle(btn, "off", "on");
  restyle(icon, "fa-times", "fa-check");
};

function setupControls(topology) {
  
  const refreshBtn = document.getElementById("refreshBtn");
  refreshBtn.addEventListener("click", () => {
    topology.toggleRefresh();
    toggleBtnAppearance(refreshBtn);
  });

  const inactiveBtn = safeGetById("inactiveBtn");
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
  
};

document.addEventListener("DOMContentLoaded", async () => {
  const topology = new Topology();
  setupControls(topology);
  await topology.render();
});

