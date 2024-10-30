// ui_setup.js
import { GuacNode } from "./api_data";

export { TopologySetup, GraphAssets };

const getSvgDimensions = (svg) => {
  const dimensions = svg.node().getBoundingClientRect();
  return { width: dimensions.width, height: dimensions.height };
};

class TopologySetup {
  /**
   * finds the svg tag and appens the "g" tag
   * which is the container for the entire topology
   * @returns {Object} svg and container
   */
  static initSVG() {
    const svg = d3.select("svg");
    const container = svg.append("g");
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

    const zoom = d3.zoom().scaleExtent([0.5, 5]).on("zoom", handleZoom);
    svg.call(zoom);
  }
  /**
   * initalizes the simulation used
   * for the collision physics of the nodes
   * and relies on getSvgDimensions(svg)
   * @param {*} svg
   * @returns {Object} simulation
   */
  static setupSimulation(svg) {
    12;
    const { width, height } = getSvgDimensions(svg);
    return d3
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
    this.edge = svg.append("g").classed("node-edge", true).selectAll("line");
    this.node = svg.append("g").selectAll("circle");
    this.label = svg.append("g").classed("node-label", true).selectAll("text");
    this.nodePositions = new Map();
  }
  setEdges(linkData) {
    this.edge = this.edge.data(linkData).join("line");
  }

  /**
   * 
   * @param {GuacNode[]} dataNodes 
   * @param {function} dragFunc 
   * @param {callback} callback 
   */
  setNodes(dataNodes, dragFunc, callback) {
    this.node = this.node
      .data(dataNodes)
      .join("circle")
      .attr("r", (d) => d.config.size)
      .attr("fill", (d) => d.config.color)
      .call(dragFunc)
      .on("click", (d) => {
        callback(d);
      });
  }

  setLabels(dataNodes) {
    this.label = this.label
      .data(dataNodes)
      .join("text")
      .text((d) => d.name || "Unamed Node")
      .attr("dy", (d) => d.config.size * 1.5);
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
    this.node
      .attr("cx", (d) => d.x)
      .attr("cy", (d) => d.y);
    this.label
      .attr("x", (d) => d.x)
      .attr("y", (d) => d.y);
  }
}

/* NOTES
  1. initalize the svg & zoom
  2. set up zoom 
  3. setup the simulation
  4. setup the drag events
  5. setup the links => class "node-edge"
    old way 
      svg>g>"line"
      joined the predefined link attribute with 
      the {soiurce, target} and on simulation tick
      updated the x1, y1, x2, y2 attributes
        y1, x1 source
        x2, y2 target
    other way
      .attr("stroke", "#999")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", 2);

  6. setup dataNodes 
     old way 
     svg>g>circle
     - used data returned from api with predefined asset 
    attr("r", (d) => d.size)
    attr("fill", (d) => color[d.weight])
    call(drag)
    .on("click" 
      it checked if cntrl key was pressed as well
        added "selected" class if it was 
      otherwise
        removed "selected" class from all other dataNodes 
      the node data would appear to the side
      would add all selected dataNodes 
  
  old way remaining steps 
    define title for the labels of the dataNodes

    define connections for the number of connections on 
    a node 


*/
