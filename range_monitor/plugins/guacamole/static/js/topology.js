// static/js/topology.js
import { GuacNode, ConnectionGroup, GuacContext } from "./topology/api_data.js";
import { TopologySetup, GraphAssets } from "./topology/ui_setup.js";


let updateID = null;
let selectedIdentifiers = [];

const ControlState = function () {
  this.status = true;
  this.toggle = function () {
    this.status = !this.status;
  };
};
const TopologyStatus = {
  refreshEnabled: new ControlState(),
  showInactive: new ControlState(),
};

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

const haveIdentifiers = () => {
  if (selectedIdentifiers.length === 0) {
    alert("Please select a connection node first!");
    return false;
  }
  return true;
};

const xhrRequestTo = (endpoint) => {
  const apiEndpoint = `/guacamole/api/${endpoint}`;
  const xhrGuac = new XMLHttpRequest();
  xhrGuac.open("POST", apiEndpoint, true);
  xhrGuac.setRequestHeader("Content-Type", "application/json");
  return xhrGuac;
};

const restyle = (tag, oldStyle, newStyle) => {
  tag.classList.replace(oldStyle, newStyle);
};

class ButtonHandler {
  static connectBtn() {
    const xhr = xhrRequestTo("connect-connections");
    xhr.onreadystatechange = function () {
      if (xhr.readyState !== XMLHttpRequest.DONE) {
        return;
      }
      // when ready but not 200
      if (xhr.status !== 200) {
        alert(xhr.responseText);
        return;
      }
      var response = JSON.parse(xhr.responseText);
      var url = response.url;
      var token = response.token;
      var link = `${url}?token=${token}`;
      window.open(link, "_blank");
      console.log(response);
    };
    var data = JSON.stringify({ identifiers: selectedIdentifiers });
    xhr.send(data);
  }
  static killBtn() {
    const xhr = xhrRequestTo("kill-connections");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        console.log(response);
      } else if (xhr.readyState === XMLHttpRequest.DONE) {
        alert(xhr.responseText);
      }
    };
    const data = JSON.stringify({ identifiers: selectedIdentifiers });
    xhr.send(data);
  }
  static timelineBtn() {
    window.open(selectedIdentifiers[0] + "/connection_timeline", "_blank");
  }
}

/**
 * @class NodeControls
 * @description responsible for the events & state nodes
 * @property {HTMLElement} connectBtn - the connect button
 * @property {HTMLElement} killBtn - the kill button
 * @property {HTMLElement} timelineBtn - the timeline button
 * @method addEvents - adds events to the buttons
 */
class NodeControls {
  constructor() {
    this.connectBtn = safeGetById("connect-button");
    this.killBtn = safeGetById("kill-button");
    this.timelineBtn = safeGetById("timeline-button");
  }
  /**
   * adds the event listeners to the btns
   * logic for each btn is in ButtonHandler
   */
  addEvents() {
    this.connectBtn.addEventListener("click", () => {
      if (!haveIdentifiers()) {
        return;
      }
      ButtonHandler.connectBtn();
    });

    this.killBtn.addEventListener("click", () => {
      if (!haveIdentifiers()) {
        return;
      }
      ButtonHandler.killBtn();
    });

    this.timelineBtn.addEventListener("click", () => {
      if (!haveIdentifiers()) {
        return;
      }
      ButtonHandler.timelineBtn();
    });
  }
}
class ControlsHandler {
  static onRefresh() {
    TopologyStatus.refreshEnabled.toggle();
    if (TopologyStatus.refreshEnabled) {
      updateTopology();
      updateID = setInterval(updateTopology, 5000);
      return;
    }
    clearInterval(updateID);
    updateID = null;
  }
  static onInactive() {
    TopologyStatus.showInactive.toggle();
    updateTopology(true);

    svg.selectAll("circle").classed("selected", false);
    nodeDataContainer.innerHTML = null;
    selectedIdentifiers = null;

    if (TopologyStatus.refreshEnabled) {
      clearInterval(updateID);
      updateID = setInterval(updateTopology, 5000);
    }
  }
  static updateDisplay(btn) {
    const icon = btn.querySelector(".opt-icon");
    if (btn.classList.contains("on")) {
      restyle(btn, "on", "off");
      restyle(icon, "fa-check", "fa-times");
      return;
    }
    restyle(btn, "off", "on");
    restyle(icon, "fa-times", "fa-check");
  }
  static toggleMenu(menuTag) {
    if (menuTag.classList.contains("active")) {
      restyle(menuTag, "active", "inactive");
      return;
    }
    restyle(menuTag, "inactive", "active");
  }
}



/**
 * @class TopologyControls
 * @description responsible for controlling whats shown on the topology
 * @property {HTMLElement} refreshBtn - the refresh button
 * @property {HTMLElement} inactiveBtn - the inactive button
 */
class TopologyControls {
  constructor() {
    this.refreshBtn = safeGetById("refreshBtn");
    this.inactiveBtn = safeGetById("inactiveBtn");
    this.menu = safeGetById("settingsMenu");
    this.toggler = safeGetById("menuToggler");
  }
  addEvents() {
    this.refreshBtn.addEventListener("click", () => {
      ControlsHandler.onRefresh();
      ControlsHandler.updateDisplay(this.refreshBtn);
    });
    this.inactiveBtn.addEventListener("click", () => {
      ControlsHandler.onInactive();
      ControlsHandler.updateDisplay(this.inactiveBtn);
    });

    this.toggler.addEventListener("click", () => {
      ControlsHandler.toggleMenu(this.menu);
    });
  }
}



const fetchGuacData = async () => {
  const guacEndpoint = "api/topology_data";
  const response = await fetch(guacEndpoint);
  if (!response.ok) {
    throw new TopologyError(`HTML Error: ${guacEndpoint}`);
  }
  const jsonData = await response.json();
  return jsonData;
};



class Topology {
  constructor() {

  }
}





const setupDrag = (updateId) => {
  function dragStarted(event, d) {
    if (!event.active) {
      simulation.alphaTarget(0.1).restart();
    }
    d.fx = d.x;
    d.fy = d.y;
    if (updateId) {
      clearInterval(updateId);
      // ???
    }
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
    if (TopologyStatus.refreshEnabled) {
      updateId = setInterval(updateTopology, 5000);
    }
  }
  return d3
    .drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded);
};

/**
 * Using the JSON response for the Guacamole API
 * and the TopologyStatus, it filters out nodes
 * that either are active or inactive.
 * @param {Object} dataNodes
 * @returns {Array[Object]}
 */
const getNodesByStatus = (dataNodes) => {
  const nodeIsActive = (node) => {
    return node.identifier && node.activeConnections > 0;
  };

  if (TopologyStatus.showInactive.status) {
    return dataNodes.filter((node) => node.identifier);
  } else {
    return dataNodes.filter(nodeIsActive);
  }
};

const updateTopology = (start = false) => {
  console.log("Updating topology...");
  fetchGuacData()
    .then((data) => {
      everything(start, data);
    })
    .catch((err) => {
      console.error(err);
    });
};

// needs a nodaDataContainer, optionsContainer & selectedIdentifers
const onNodeClick = function (d) {
  if (d.ctrlKey || d.metaKey) {
    d3.select(this).classed("selected", !d3.select(this).classed("selected"));
  } else {
    svg.selectAll("circle").classed("selected", false);
    d3.select(this).classed("selected", true);
  }
  let nodeData = d.target.__data__.data;
  let htmlData = convertToHtml(nodeData);
  nodeDataContainer.innerHTML = htmlData;

  let selectedNodes = svg.selectAll(".selected").data();
  selectedIdentifiers = [];
  selectedNodes.forEach((node) => {
    if (node.protocol) {
      selectedIdentifiers.push(node.identifier);
    }
  });

  if (selectedIdentifiers.length === 0) {
    optionsContainer.style.display = "none";
  } else {
    optionsContainer.style.display = "block";
  }
  console.log(selectedIdentifiers);
};

/**
 * @class NodeConfig
 * @param {number|NodeWeight} weight - The weight of the node.(1-5)
 * @property {number} size - The size of the node.
 * @property {string} color - The RGB color of the node corresponding to colors.
 */

const getObjectLength = (obj) => Object.keys(obj).length;

const everything = (start, data) => {
  if (!data) return;

  const context = new TopologyContext(data.nodes);
  context.buildLinks();

  // ^- From -v
  // const results = countNullPropertiesAcrossObjects(nodes);
  // console.table(results);

  // join the links together
  link = link.data(context.links).join("line");

  context.initPreviousPositions();

  const previousPositions = context.previousPositions;

  // set the node data
  node = node
    .data(context.nodes)
    .join("circle")
    .attr("r", (d) => d.size)
    .attr("fill", (d) => colors[d.weight])
    .call(drag)
    .on("click", (d) => {
      onNodeClick(d);
    });

  // set the node titles, needs nodes
  title = title
    .data(context.nodes)
    .join("text")
    .text((d) => d.name || "Unknown")
    .attr("dy", (d) => d.size * 1.5)
    .style("font-size", (d) => d.size / 2);

  connections = connections
    .data(context.nodes)
    .join("text")
    .text((d) => d.activeConnections)
    .attr("dy", (d) => d.size / 2)
    .style("font-size", (d) => d.size * 1.5)
    .style("fill", (d) => (d.protocol ? "white" : "black"));

  simulation.nodes(context.nodes);

  let isNewNodes = false;
  context.nodes.forEach((node) => {
    const previousPosition = previousPositions.get(
      `${node.identifier}${node.type}`
    );
    if (previousPosition) {
      Object.assign(node, previousPosition);
    } else {
      isNewNodes = true;
    }
  });

  simulation.force("link").links(context.links);
  if (start === true) {
    simulation.alpha(1).restart();
  } else if (isNewNodes) {
    simulation.alpha(0.1).restart();
  } else {
    simulation.alpha(0).restart();
  }
  simulation.on("tick", () => {
    link
      .attr("x1", (d) => d.source.x)
      .attr("y1", (d) => d.source.y)
      .attr("x2", (d) => d.target.x)
      .attr("y2", (d) => d.target.y);

    node.attr("cx", (d) => d.x).attr("cy", (d) => d.y);
    title.attr("x", (d) => d.x).attr("y", (d) => d.y);

    connections.attr("x", (d) => d.x).attr("y", (d) => d.y);
  });
};

updateTopology(true);
updateID = setInterval(updateTopology, 5000);




/**
 * Calculates the weight of a given node based on its properties.
 *
 * @param {Object} node - The node object to calculate the weight for.
 * @return {number} The weight of the node.
 */
let btns;
try {
  btns = new NodeControls();
  btns.addEvents();
} catch (err) {
  console.error(`TopologyButton initalization failed.\n${err}`);
}

let controls;
try {
  controls = new TopologyControls();
  controls.addEvents();
} catch (err) {
  console.error(`TopologyControls initalization failed.\n${err}`);
}