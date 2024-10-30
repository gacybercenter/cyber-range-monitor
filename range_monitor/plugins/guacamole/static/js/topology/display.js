// topology/display.js
import { GuacNode, ConnectionGroup, GuacContext } from "./api_data.js";
import { TopologySetup, GraphAssets } from "./ui_setup.js";

export { Topology, TopologyController };

class TopologyError extends Error {
  constructor(message) {
    super(
      `TopologyError: something went wrong in the topology.\n[INFO] - ${message}`
    );
    this.name = "TopologyError";
  }
}

/**
 *
 * @param {TopologyController} controller
 * @param {Topology} topology
 * @returns {function} - a drag event handler
 */
const setupDrag = (controller, topology) => {
  function dragStarted(event, d) {
    if (!event.active) {
      simulation.alphaTarget(0.1).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
    controller.resetInterval(false);
  }
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  function dragEnded(event, d) {
    if (!event.active) {
      topology.simulation.alphaTarget(0.1).restart();
    }
    d.fx = null;
    d.fy = null;
    if (controller.refreshEnabled) {
      controller.setInterval(() => {
        topology.render();
      }, 5000);
    }
  }
  return d3
    .drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded);
};

/**
 *
 * @param {*} d
 * @param {Topology} topology
 */
const onNodeClick = (d, topology) => {
  if (d.ctrlKey || d.metaKey) {
    d3.select(this).classed("selected", !d3.select(this).classed("selected"));
  } else {
    topology.svg.selectAll("circle").classed("selected", false);
    d3.select(this).classed("selected", true);
  }
  let selected = topology.svg.selectAll(".selected").data();
  const idsAdded = topology.controller.buildSelectedIds(selected);
  // ^- not finished yet 
};

/**
 * @class TopologyController
 * @description
 * responsible for managing the topology state
 * and control flow
 * @property {boolean} refreshEnabled - whether the topology is refreshing
 * @property {boolean} showInactive - whether inactive nodes should be shown
 * @property {string[]} selectedIdentifiers - the selected nodes
 * @property {number|null} updateInterval - the interval for updating the topology
 */
class TopologyController {
  constructor() {
    this.refreshEnabled = true;
    this.showInactive = true;
    this.selectedIdentifiers = [];
    this.updateInterval = null;
  }
  /**
   * clears the updateInterval property
   * @param {boolean} shouldDisable - set updateInterval to null
   */
  resetInterval(shouldDisable = true) {
    if (!this.updateInterval) return;

    clearInterval(this.updateInterval);
    if (shouldDisable) {
      this.updateInterval = null;
    }
  }
  /**
   * sets the updateInterval property
   * for updating the topology
   * @param {callback} callback
   * @param {number} ms
   */
  setInterval(callback, ms = 5000) {
    this.updateInterval = setInterval(callback, ms);
  }
  /**
   * fetches the guac data from the API
   * endpoint
   * @returns {object}
   */
  async fetchGuacData() {
    const guacEndpoint = "api/topology_data";
    const response = await fetch(guacEndpoint);
    if (!response.ok) {
      throw new TopologyError("Guac API rejected request.");
    }
    return await response.json();
  }

  getGuacNodes() {
    try {
      const guacDump = this.fetchGuacData();
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
    console.log(`Type of nodes: ${typeof nodes}`);
    const nodeIsActive = (node) => {
      return node.identifier && node.activeConnections > 0;
    };

    if (this.showInactive) {
      return nodes.filter((node) => node.identifier);
    } else {
      return nodes.filter(nodeIsActive);
    }
  }
  buildSelectedIds(nodeData) {
    this.selectedIdentifiers = [];
    nodeData.forEach((node) => {
      if (node.protocol) {
        this.selectedIdentifiers.push(node.identifier);
      }
    });
    return this.selectedIdentifiers.length;
  }
}

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

    this.controller = new TopologyController();
    this.drag = setupDrag(this.controller, this);

    this.assets = new GraphAssets(svg);
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
  render() {
    const nodes = this.controller.getGuacNodes();

    const filteredNodes = this.controller.filterNodesByStatus(nodes);
    let alphaValue;
    if (!this.context) {
      console.log("initializing context");
      alphaValue = 1;
      this.context = new GuacContext();
      this.initializeUI(alphaValue, filteredNodes);
      return;
    }

    const contextChanged = this.context.updateNodes(filteredNodes);
    alphaValue = contextChanged ? 0.1 : 0;
    this.initializeUI(alphaValue, filteredNodes);
  }

  /**
   * @param {number} alphaValue - the force to apply to the nodes
   * @param {Object[]} filteredNodes - inactive or active nodes
   */
  initializeUI(alphaValue, filteredNodes) {
    this.context.buildContext(filteredNodes);

    this.assets.setEdges(this.context.links);
    this.assets.setNodes(this.context.guacNodes, this.drag,  (d) => {
      onNodeClick(d, this);
    });

    this.assets.setLabels(this.context.guacNodes);

    this.simulation.nodes(this.context.guacNodes);
    this.simulation.force("link").links(this.context.edges);
    this.simulation.alpha(alphaValue).restart();
    this.simulation.on("tick", () => {
      this.assets.onTick();
    });

    console.log("context built");
  }
  toggleRefresh() {
    this.controller.refreshEnabled = !this.controller.refreshEnabled;
    if (this.controller.refreshEnabled) {
      this.render();
      this.controller.setInterval(() => {
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
      this.controller.setInterval(() => {
        this.render();
      }, 5000);
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
