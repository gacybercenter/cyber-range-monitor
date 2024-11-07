// ui_setup.js
import { Modal } from "./node-modal.js/guac-modal.js";
import { ConnectionModals } from "./node-modal.js/modal-assets.js";
import { ConnectionNode } from "./api_data.js";
export { TopologySetup, GraphAssets };

class EventHandlers {
  /**
   * @param {*} event
   * @param {set<ConnectionNode>} userSelection
   * @returns
   */
  static nodeClick(event, userSelection) {
    const target = event.target;
    const untoggleSelected = () => {
      d3.selectAll(".selected").classed("selected", false);
      d3.select(target).classed("selected", true);
    };

    if (event.ctrlKey || event.metaKey) {
      d3.select(target).classed(
        "selected",
        !d3.select(target).classed("selected")
      );
    } else {
      untoggleSelected();
    }
    
    let current = target.__data__;
    userSelection.clear();
    
    if(current.isRoot()) {
      console.warn("Root node cannot be selected");
      d3.selectAll(".selected").classed("selected", false);
      return;
    }

    if (current.isGroup()) { 
      userSelection.add(current);
      return;
    } 
    const selected = d3.selectAll(".selected").data();
    selected.forEach((node) => {
      userSelection.add(node);
    });
  }

  /**
   * triggers on middle click
   * @param {Set<string>} userSelection
   * @param {ConnectionNode[]} nodes
   * @param {Map<string, ConnectionNode>} nodeMap
   */
  static showNodeModal(userSelection, nodes, nodeMap) {
    const modal = new Modal();
    let modalData, title;
    const selection = Array.from(userSelection);
    const first = selection[0];
    if (first.isRoot()) {
      return;
    } else if (first.isGroup()) {
      modalData = ConnectionModals.connectionGroup(first, nodes, nodeMap);
      title = `Connection Group: ${first.name}`;
    } else if (userSelection.size === 1) {
      modalData = ConnectionModals.singleConnection(first, nodeMap);
      title = `Connection Details: ${first.name}`;
    } else {
      modalData = ConnectionModals.manyConnections(selection, nodeMap);
      title = `Selected Connections Overview (${selection.length})`;
    }
    modal.init(title, modalData);
    modal.openModal();
  }
}

class TopologySetup {
  /**
   * finds the svg tag and appens the "g" tag
   * which is the container for the entire topology
   * @returns {Object} svg and container
   */
  static initSVG() {
    const svg = d3.select("svg");
    const container = svg.append("g");
    TopologySetup.setupZoom(svg, container);
    return { svg, container };
  }
  /**
   * sets up the zooming funcitonality
   * for the topology and updates the UI
   * so the user can see the zoom level
   * every time that they zoom
   * @param {*} svg
   * @param {*} container
   */
  static setupZoom(svg, container) {
    const handleZoom = (event) => {
      container.attr("transform", event.transform);
      const zoomPercent = Math.round(event.transform.k * 100);
      d3.select(".zoom-scale").text(`${zoomPercent}%`);
    };

    svg.call(
      d3
        .zoom()
        .scaleExtent([0.5, 5])
        .on("zoom", (event) => {
          handleZoom(event);
        })
    );
  }

  /**
   * initalizes the simulation used
   * for the collision physics of the nodes
   * and relies on getSvgDimensions(svg)
   * @param {*} svg
   * @returns {Object} simulation
   */
  static setupSimulation(svg) {
    const { width, height } = svg.node().getBoundingClientRect();
    return d3
      .forceSimulation()
      .force(
        "link",
        d3
          .forceLink()
          .id((d) => d.identifier)
          .distance(100) // pull a link has
      )
      .force(
        "charge",
        d3.forceManyBody().strength(-400) // charge of each node
      )
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force(
        "collision",
        d3.forceCollide().radius((d) => d.size + 10)
      );
  }
}
/**
 * @class GraphAssets
 * @property {Object} edge - The edges of the graph.
 * @property {Object} node - The nodes of the graph.
 * @property {Object} label - The labels of the nodes.
 * @property {Map} nodePositions - A map of node positions keyed by node identifier.
 */
class GraphAssets {
  constructor(svg) {
    this.edge = svg.append("g").attr("stroke-width", 1).selectAll("line");
    this.node = svg.append("g").selectAll("circle");
    this.label = svg
      .append("g")
      .attr("text-anchor", "middle")
      .attr("pointer-events", "none")
      .selectAll("text");
  }
  createLinks(linkData, nodeMap) {
    this.edge = this.edge
      .data(linkData)
      .join("line")
      .attr("class", (d) => {
        const target = nodeMap.get(d.target);
        const status = target.isActive() ? "active-edge" : "inactive-edge";
        return `${status} ${d.source}`;
      });
  }

  /**
   *
   * @param {GuacNode[]} dataNodes
   * @param {function} dragFunc
   * @param {callback} callback
   */

  /**
   *
   * @param {*} dataNodes
   * @param {*} dragFunc
   * @param {Object{}} context
   */
  setNodes(dataNodes, dragFunc, context) {
    let { userSelection, nodes, nodeMap } = context;
    this.node = this.node
      .data(dataNodes)
      .join("circle")
      .classed("conn-node", true)
      .attr("r", (d) => d.size)
      .attr("fill", (d) => d.color)
      .call(dragFunc)
      .on("click", function (event) {
        event.preventDefault();
        EventHandlers.nodeClick(event, userSelection);
      })
      .on("auxclick", (event) => {
        event.preventDefault();
        EventHandlers.showNodeModal(userSelection, nodes, nodeMap);
      });
  }
  setLabels(dataNodes) {
    this.label = this.label
      .data(dataNodes)
      .join("text")
      .text((d) => d.name || "Unamed Node")
      .attr("font-size", (d) => d.size / 2 + "px")
      .attr("dy", (d) => d.size + 5)
      .attr("class", (d) => (d.isActive() ? "active-label" : "inactive-label"));
  }

  /**
   * logic for when the simulation ticks
   */
  onTick() {
    this.edge
      .attr("x1", (d) => d.source.x)
      .attr("x2", (d) => d.target.x)
      .attr("y1", (d) => d.source.y)
      .attr("y2", (d) => d.target.y);
    this.node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    this.label.attr("x", (d) => d.x).attr("y", (d) => d.y);
  }
}
export class NavigationHints {
  static hints = [
    {
      about: "To navigate the topology and drag nodes",
      keys: ["Click", "Drag"],
    },
    {
      about: "To zoom in and out of the topology",
      keys: ["Scroll"],
    },
    {
      about: "Double click a node to view its controls and more information",
      keys: ["Double Click"],
    },
    {
      about: "To select multiple nodes at once",
      keys: ["Ctrl", "Click"],
    },
    {
      about: "To control all selected nodes",
      keys: ["Ctrl", "Alt"],
    },
    {
      about: "On a node to access controls and connection information",
      keys: ["Middle Click"],
    },
  ];
  static keyMap = {
    CTRL: "Ctrl",
    ALT: "Alt",
    SHIFT: "Shift",
    COMMAND: "Cmd",
    META: "Cmd", // For Mac users
    CLICK: "Click",
    "DOUBLE CLICK": "Double Click",
    "MIDDLE CLICK": "Middle Click",
    SCROLL: "Scroll",
    DRAG: "Drag",
    DROP: "Drop",
  };

  static init() {
    this.renderHints();
    this.setupToggleButton();
    this.setupEventListeners();
  }

  static renderHints() {
    const container = d3.select("#nav-hints");

    const navHints = container
      .selectAll(".nav-hint")
      .data(this.hints)
      .enter()
      .append("div")
      .attr("class", "nav-hint");

    navHints.each(function (d) {
      const hint = d3.select(this);

      d.keys.forEach((key, index) => {
        const isModifier = ["Ctrl", "Alt", "Shift", "Cmd"].includes(key);
        hint
          .append("span")
          .attr("class", isModifier ? "key modifier" : "key")
          .text(NavigationHints.formatKey(key));

        if (d.keys.length > 1 && index < d.keys.length - 1) {
          hint.append("span").attr("class", "plus-sign").text("+");
        }
      });

      hint.append("span").attr("class", "description").text(d.about);
    });
  }
  static formatKey(key) {
    const upperKey = key.toUpperCase();
    return (
      this.keyMap[upperKey] || (key.length === 1 ? key.toUpperCase() : key)
    );
  }
  static highlightKeys(keyLabel) {
    const keys = d3.selectAll(".key").filter(function () {
      return d3.select(this).text() === keyLabel;
    });

    keys.classed("highlighted", true);

    setTimeout(() => {
      keys.classed("highlighted", false);
    }, 200);
  }

  static setupToggleButton() {
    const toggleButton = d3.select("#hideHints");
    const navHintsContainer = d3.select("#nav-hints");

    toggleButton.on("click", () => {
      const isHidden = navHintsContainer.classed("hidden");
      navHintsContainer.classed("hidden", !isHidden);
      toggleButton.classed("rotated", !isHidden);
    });
  }

  static setupEventListeners() {
    document.addEventListener("keydown", (event) => {
      const keysPressed = this.getKeysPressed(event);
      keysPressed.forEach((key) => {
        this.highlightKeys(key);
      });
    });

    $(document).on("click", () => {
      this.highlightKeys("Click");
    });

    $(document).on("dblclick", () => {
      this.highlightKeys("Double Click");
    });

    $(document).on("wheel", () => {
      this.highlightKeys("Scroll");
    });
    $(document).on("auxclick", () => {
      this.highlightKeys("Middle Click");
    });

    document.addEventListener("mouseup", (event) => {
      if (event.target.classList.contains("draggable")) {
        this.highlightKeys("Drop");
      }
    });
  }
  static getKeysPressed(event) {
    const keysPressed = [];
    if (event.ctrlKey) {
      keysPressed.push("Ctrl");
    }
    if (event.altKey) {
      keysPressed.push("Alt");
    }
    if (event.shiftKey) {
      keysPressed.push("Shift");
    }
    if (event.metaKey) {
      keysPressed.push("Cmd");
    }
    if (event.type === "auxclick") {
      keysPressed.push("Middle Click");
    }

    let mainKey = event.key;
    if (mainKey === " ") {
      mainKey = "Space";
    } else if (mainKey.toLowerCase() === "scroll") {
      mainKey = "Scroll";
    } else {
      mainKey = mainKey.toUpperCase();
    }
    return keysPressed;
  }
}


export class StatusUI {
  constructor() {
    this.$statusContent = $(".status-content");
    this.$statusMsg = this.$statusContent.find("#statusMsg");
    this.loadInterval = null;
  }
  loading() {
    const msgs = ["Loading.", "Loading..", "Loading..."];
    let index = 0;
    this.loadInterval = setInterval(() => {
      index = (index + 1) % msgs.length;
      this.$statusMsg.fadeOut(200, function () {
        $(this).text(msgs[index]).fadeIn(200);
      });
    }, 700);
  }
  hide() {
    $(".status-ui").fadeOut(500, function () {
      $("svg").removeClass("hidden");
    });
  }
  /**
   *
   * @param {string} errorMsg
   * @returns {JQuery<HTMLElement>} - the retry button to add an event listener 2
   */
  toErrorMessage(errorMsg) {
    clearInterval(this.loadInterval);
    this.$statusContent
      .find("i")
      .removeClass(StatusUI.LOAD_FAS)
      .addClass(StatusUI.ERROR_FAS);

    const msg =
      errorMsg || "An error occurred rendering the topology, please try again.";

    this.$statusMsg.text(msg);
    const $retry = $("<div id='retry-hold'></div>");
    const $btn = $("<button id='retryBtn'>").html(`
      <i class="fa-solid fa-arrow-rotate-right"></i>
      Retry 
    `);
    $retry.append($btn);
    this.$statusContent.append($retry);
    return $btn;
  }
  toLoading() {
    this.$statusContent
      .find("i")
      .removeClass(StatusUI.ERROR_FAS)
      .addClass(StatusUI.LOAD_FAS);
    this.$statusContent.find("#statusMsg").text("Loading.");
    $("#retry-hold").remove();
    this.loading();
  }
}
