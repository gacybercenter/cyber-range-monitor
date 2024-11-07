// topology/display.js
import { ContextHandler } from "./api_data.js";
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
      controller.updateInterval(() => {
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
 * @class TopologyController
 * @description
 * responsible for managing the topology state
 * and control flow
 * @property {boolean} refreshEnabled - whether the topology is refreshing
 * @property {boolean} showInactive - whether inactive nodes should be shown
 * @property {string[]} userSelection - the selected nodes
 * @property {number|null} updateId - the interval for updating the topology
 */
class TopologyController {
  constructor() {
    this.refreshEnabled = true;
    this.showInactive = true;
    this.userSelection = new Set();
    this.updateId = null;
  }
  /**
   * clears the updateId property
   * @param {boolean} shouldDisable - set updateId to null
   */
  resetInterval(shouldDisable = true) {
    if (!this.updateId) {
      return;
    }
    clearInterval(this.updateId);
    if (shouldDisable) {
      this.updateId = null;
    }
  }
  /**
   * sets the updateId property
   * for updating the topology
   * @param {callback} callback
   * @param {number} ms
   */
  updateInterval(callback, ms = 5000) {
    this.updateId = setInterval(callback, ms);
  }
  /**
   * fetches the guac data from the API
   * endpoint
   * @returns {object}
   */
  async fetchGuacAPI() {
    const guacURL = "api/topology_data";
    const response = await fetch(guacURL);
    const data = await response.json();
    if (!data) {
      throw new TopologyError("No data returned by the API");
    }
    if (!data.nodes) {
      throw new TopologyError("No nodes returned by the API");
    }
    return data.nodes;
  }

  /**
   * filters out nodes based on "showInactive"
   * prop
   * @param {Object[]} nodes
   * @returns {Object[]}
   */

  filterNodesByStatus(nodes) {
    let predicate = (node) => {
      return node.identifier && node.activeConnections > 0;
    };

    if (this.showInactive) {
      predicate = (node) => {
        return node.identifier;
      };
    }
    const output = [];
    nodes.forEach((node) => {
      if (predicate(node)) {
        output.push(node);
      }
    });
    return output;
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
    this.isFirstRender = true;

    this.controller = new TopologyController();
    this.drag = setupDrag(this.controller, this);
    this.assets = new GraphAssets(this.container);
  }
  async render(isFirstRender = false) {
    const nodes = await this.controller.fetchGuacAPI();
    const nodeData = this.controller.filterNodesByStatus(nodes);
    const parsedNodes = ContextHandler.getContext(nodeData);
    this.renderTopology(parsedNodes, isFirstRender);
  }

  renderTopology(parsedNodes, isFirstRender) {
    const { nodes, edges, nodeMap } = parsedNodes;
    ContextHandler.truncateNodeNames(nodes, nodeMap);
    this.assets.createLinks(edges, nodeMap);
    // NOTE you MUST set the prevPositions here or Exception, very fun!!
    const prevPositions = new Map(
      this.assets.node
        .data()
        .map((d) => [`${d.identifier}`, { x: d.x, y: d.y }])
    );

    const context = {
      userSelection: this.controller.userSelection,
      nodes: nodes,
      nodeMap: nodeMap,
    };

    this.assets.setNodes(nodes, this.drag, context);
    this.assets.setLabels(nodes);
    this.simulation.nodes(nodes);

    let shouldRefresh = false;
    nodes.forEach((node) => {
      const prev = prevPositions.get(node.identifier);
      if (prev) {
        Object.assign(node, prev);
      } else {
        shouldRefresh = true;
      }
    });

    this.simulation.force("link").links(edges);
    let alphaValue;
    if(isFirstRender) {
      alphaValue = 1;
    } else if(shouldRefresh) {
      alphaValue = 0.1;
    } else {
      alphaValue = 0;
    }
    this.simulation.alpha(alphaValue).restart();
    this.simulation.on("tick", () => {
      this.assets.onTick();
    });
    this.isFirstRender = false;
  }
  toggleRefresh() {
    this.controller.refreshEnabled = !this.controller.refreshEnabled;
    if (this.controller.refreshEnabled) {
      this.controller.updateInterval(async () => {
        await this.render();
      });
    } else {
      this.controller.resetInterval();
    }
  }
  toggleInactive() {
    this.controller.showInactive = !this.controller.showInactive;
    (async () => {
      await this.render();
    })();
    if (this.controller.refreshEnabled) {
      this.controller.updateInterval(async () => {
        await this.render();
      }, 5000);
    }
  }
}
