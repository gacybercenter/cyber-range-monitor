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
      topology.simulation.alphaTarget(0.1).restart();
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
  fetchGuacData() {
    const guacEndpoint = "api/topology_data";
    return fetch(guacEndpoint)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        if (!data) {
          throw new TopologyError("No data returned by the API");
        }
        if (!data.nodes) {
          throw new TopologyError("No nodes returned by the API");
        }
        const nodes = data.nodes;
        console.log("fetched => ", JSON.stringify(nodes));
        return nodes;
      })
      .catch((err) => {
        console.log(`Error fetching guac data: ${err}`);
      });
  }

  /**
   * filters out nodes based on "showInactive"
   * prop
   * @param {Object[]} nodes
   * @returns
   */

  filterNodesByStatus(nodes) {
    let predicate = (node) => {
      return node.identifier && node.activeConnections > 0;
    };
    if (this.showInactive) {
      predicate = (node) => {
        return node.identifier !== null;
      };
    }
    return nodes.filter(predicate);
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
    this.simulation = TopologySetup.setupSimulation(svg);

    this.controller = new TopologyController();
    this.drag = setupDrag(this.controller, this);

    this.assets = new GraphAssets(this.container);
    this.context = null;
    this.positions = null;
    this.controller.setInterval(() => {
      this.render();
    }, 5000);
  }

  getPositions() {
    console.log(`Node data: ${this.assets.node.data()}`);
    return new Map(
      this.assets.node.data().map((d) => {
        [`${d.name}-${d.type}`, { x: d.x, y: d.y }]
      })
    );
  }
  render() {
    this.controller
      .fetchGuacData()
      .then((nodes) => {
        this.renderData(nodes);
      })
      .catch((err) => {
        console.log(err.stack);
        console.log(`Rendering error ${err}`);
      });
  }

  renderData(nodes) {
    const filteredNodes = this.controller.filterNodesByStatus(nodes);
    let start = false;
    if (!this.context) {
      this.context = new GuacContext();
      start = true;
    } 
    this.initializeUI(start, filteredNodes);
  }

  /**
   * @param {number} alphaValue - the force to apply to the nodes
   * @param {Object[]} filteredNodes - inactive or active nodes
   */
  initializeUI(start, filteredNodes) {
    let alphaValue;
    if(start) {
      this.positions = this.getPositions();
      this.context.buildContext(filteredNodes);
      alphaValue = 1;
    } else {
      this.context.updateContext(filteredNodes);
      alphaValue = 0.1;
    }
    this.context.shrinkEndpointNames();
    

    console.log("Building context ");
    this.assets.setEdges(this.context.edges);
    
    this.assets.setNodes(this.context.guacNodes, 
      this.drag, (d) => {
        onNodeClick(d, this);
    });

    this.assets.setLabels(this.context.guacNodes);

    this.simulation.nodes(this.context.guacNodes);
    


    this.simulation.force("link").links(this.context.edges);
    this.simulation.alpha(alphaValue).restart();
    this.simulation.on("tick", () => {
      this.assets.onTick();
    });
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
    this.context = null;
    this.render();
    if(this.controller.refreshEnabled) {
      this.controller.setInterval(() => {
        this.render();
      }, 5000);
    }
  }
}


