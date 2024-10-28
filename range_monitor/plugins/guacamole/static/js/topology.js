// static/js/topology.js
import { GuacNode, ConnectionGroup, GuacContext } from "./topology/api_data.js";


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

const fetchGuacData = async () => {
  const guacEndpoint = "api/topology_data";
  const response = await fetch(guacEndpoint);
  if (!response.ok) {
    throw new TopologyError(`HTML Error: ${guacEndpoint}`);
  }
  const jsonData = await response.json();
  return jsonData;
};

const getSvgDimensions = (svg) => {
  const dimensions = svg.node().getBoundingClientRect();
  return { width: dimensions.width, height: dimensions.height };
};

// container for the topology itself

// for connecting, killing & timeline btns
const optionsContainer = document.getElementById("guac-options");

// used to change the inner html of the node-data div
const nodeDataContainer = document.getElementById("node-data");

// toggles refresh & inactive in > div.map

// enums, mapping node types to colors and weights (thats readable)

// maybe used later for getting node icons?
const NodeTypes = Object.freeze({
  ROOT: "ROOT",
  GUAC_GROUP: "GUAC_GROUP",
  HOST: "HOST",
  ACTIVE_ENDPOINT: "ACTIVE_ENDPOINT",
  INACTIVE_ENDPOINT: "ACTIVE_ENDPOINT",
});

const setupZoom = (topology) => {
  const { svg, container } = topology;
  const zoomHandler = (event) => {
    container.attr("transform", event.transform);
    const zoomPercent = Math.round(event.transform.k * 100);
    d3.select(".zoom-scale").text(`${zoomPercent}%`);
  };
  const zoom = d3.zoom().scaleExtent([0.5, 5]).on("zoom", zoomHandler);
  svg.call(zoom);
};

const initalizeSVG = () => {
  const svg = d3.select("svg");
  const container = svg.append("g");
  const { width, height } = getSvgDimensions(svg);
  return { svg, container, width, height };
};
const setupSimulation = (nodes, links) => {
  return d3
    .forceSimulation(nodes)
    .force(
      "link",
      d3.forceLink(links).id((d) => d.identifier)
    )
    .force(
      "charge",
      d3.forceManyBody().strength((d) => d.size * -4)
    )
    .force("center", d3.forceCenter(width / 2, height / 2));
};
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

const addGraphEdges = (container, links) => {
  return container
    .selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .classed("node-edge", true);
};
const addGraphNodes = (container, nodes) => {
  return container
    .selectAll("circle")
    .data(nodes)
    .enter()
    .append("circle")
    .classed("guac-node", true);
};
/**
 *
 * @param {*} container
 * @param {ConnectionGroup | GuacEndpoint} node
 */
const addNodeIcons = (node) => {
  node
    .append("circle")
    .attr("r", (d) => d.config.size)
    .attr("fill", (d) => d.config.color)
    .attr("stroke", "black")
    .attr("stroke-width", 1);
  node
    .append("image")
    .classed("node-icon", true)
    .attr("xlink:href", (d) => d.icon)
    .attr("width", (d) => d.config.size * 1.2)
    .attr("height", (d) => d.config.size * 1.2)
    .attr("x", (d) => -d.config.size)
    .attr("y", (d) => -d.config.size);
};

class GuacTopology {
  constructor() {
    const graph = initalizeSVG();
    this.svg = graph.svg;
    this.container = graph.container;
    this.updateId = null;
    this.selectedIdentifiers = [];
    this.simulation = null;
    this.drag = null;
  }
  /**
   * @param {GuacContext} context
   */
  init(context) {
    const { edges, allNodes } = context;
    this.simulation = setupSimulation(this.container, allNodes, edges);
    addGraphEdges(this.container, edges);
    let node = addGraphNodes(this.container, allNodes);
    addNodeIcons(node);
  }
}

svg
  .attr("width", width)
  .attr("height", height)
  .call(
    d3.zoom().on("zoom", (event) => {
      svg.attr("transform", event.transform);
    })
  )
  .append("g");

const simulation = d3
  .forceSimulation()
  .force(
    "link",
    d3.forceLink().id((d) => d.identifier)
  )
  .force(
    "charge",
    d3.forceManyBody().strength((d) => d.size * -4)
  )
  .force("center", d3.forceCenter(width / 2, height / 2));

const drag = d3
  .drag()
  .on("start", dragStarted)
  .on("drag", dragged)
  .on("end", dragEnded);

let link = svg
  .append("g")
  .attr("stroke", "black")
  .attr("stroke-width", 1)
  .selectAll("line");

let node = svg.append("g").selectAll("circle");

let title = svg
  .append("g")
  .attr("fill", "white")
  .attr("text-anchor", "middle")
  .style("font-family", "Verdana, Helvetica, Sans-Serif")
  .style("pointer-events", "none")
  .selectAll("text");

let connections = svg
  .append("g")
  .attr("fill", "white")
  .attr("text-anchor", "middle")
  .style("font-family", "Verdana, Helvetica, Sans-Serif")
  .style("pointer-events", "none")
  .selectAll("text");

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
 * Handles the start of a drag event.
 *
 * @param {Event} event - the drag event
 * @param {Object} d - the data associated with the dragged element
 */
function dragStarted(event, d) {
  if (!event.active) {
    simulation.alphaTarget(0.1).restart();
  }
  d.fx = d.x;
  d.fy = d.y;

  if (updateID) {
    clearInterval(updateID);
  }
}

/**
 * Updates the position of a dragged element.
 *
 * @param {event} event - the event object representing the drag event
 * @param {d} d - the data object associated with the dragged element
 */
function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

/**
 * Handles the event when dragging ends.
 *
 * @param {Object} event - The event object.
 * @param {Object} d - The data object.
 */
function dragEnded(event, d) {
  if (!event.active) {
    simulation.alphaTarget(0);
  }
  d.fx = null;
  d.fy = null;
  if (TopologyStatus.refreshEnabled) {
    updateID = setInterval(updateTopology, 5000);
  }
}

/**
 * Removes null values from an object, including nested objects and arrays.
 *
 * @param {object} obj - The object to remove null values from.
 * @return {object} - The object with null values removed.
 */
function removeNullValues(obj) {
  let objCopy = JSON.parse(JSON.stringify(obj)); // Create a deep copy of the object

  for (let key in objCopy) {
    if (objCopy[key] === null || objCopy[key] === "") {
      delete objCopy[key];
    } else if (typeof objCopy[key] === "object") {
      objCopy[key] = removeNullValues(objCopy[key]); // Recursively call the function for nested objects
      if (Array.isArray(objCopy[key])) {
        objCopy[key] = objCopy[key].filter(Boolean);
      }
    }
  }

  return objCopy;
}

// Function to recursively count null occurrences of properties across all objects
function countNullPropertiesAcrossObjects(objList) {
  const nullCounts = {}; // To store counts of null occurrences for each property path
  const totalObjects = objList.length;

  function traverse(obj, path = "") {
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        const currentPath = path ? `${path}.${key}` : key;

        if (value === null) {
          if (!nullCounts[currentPath]) {
            nullCounts[currentPath] = 0;
          }
          nullCounts[currentPath] += 1;
        } else if (typeof value === "object" && value !== null) {
          if (Array.isArray(value)) {
            // For arrays, traverse each element if it's an object
            value.forEach((item, index) => {
              const arrayPath = `${currentPath}[${index}]`;
              if (item === null) {
                if (!nullCounts[arrayPath]) {
                  nullCounts[arrayPath] = 0;
                }
                nullCounts[arrayPath] += 1;
              } else if (typeof item === "object") {
                traverse(item, arrayPath);
              }
            });
          } else {
            // For nested objects, recurse
            traverse(value, currentPath);
          }
        } else {
          // Non-null primitive values (number, string, boolean) are ignored here
        }
      }
    }
  }

  // Process each object in the list
  objList.forEach((obj) => {
    traverse(obj);
  });

  // Prepare the result
  const result = [];
  for (let propertyPath in nullCounts) {
    result.push({
      property: propertyPath,
      nullCount: nullCounts[propertyPath],
      totalObjects: totalObjects,
      alwaysNull: nullCounts[propertyPath] === totalObjects,
    });
  }

  return result;
}

/**
 * Converts an object into a formatted string representation.
 *
 * @param {Object} obj - The object to be converted.
 * @param {number} indent - The number of spaces to indent each level of the string representation.
 *                          Default is 0.
 * @return {string} The formatted string representation of the object.
 */
function convertToHtml(obj) {
  if (typeof obj !== "object") {
    return obj;
  }
  var html = `<h1>${obj.name || ""}</h1>`;

  /**
   * Converts an object into a formatted string representation.
   *
   * @param {Object} obj - The object to be converted.
   * @param {number} indent - The number of spaces to indent each level of the string representation.
   *                          Default is 0.
   */
  function convert(obj, indent = 0) {
    const keys = Object.keys(obj);
    for (const key of keys) {
      const value = obj[key];
      const dashIndent = "\u00A0\u00A0".repeat(indent);
      if (typeof value === "object" && value !== null) {
        html += `${dashIndent}${key}:\n`;
        convert(value, indent + 1);
      } else {
        const convertedValue =
          key === "lastActive" ? new Date(value).toLocaleString() : value;
        html += `${dashIndent}${key}: ${convertedValue}\n`;
      }
    }
  }

  convert(obj);

  return html.replace(/\n/g, "<br>").replace(/\u00A0/g, "&nbsp;");
}

/**
 * Calculates the weight of a given node based on its properties.
 *
 * @param {Object} node - The node object to calculate the weight for.
 * @return {number} The weight of the node.
 */
