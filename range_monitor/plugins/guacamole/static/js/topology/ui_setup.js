export { TopologySetup, GraphAssets };

const getSvgDimensions = (svg) => {
  const dimensions = svg.node().getBoundingClientRect();
  return { width: dimensions.width, height: dimensions.height };
};

class TopologySetup {
  static initSVG() {
    const svg = d3.select("svg");
    const container = svg.append("g");
    return { svg, container };
  }
  static setupZoom(svg, container) {
    const handleZoom = (event) => {
      container.attr("transform", event.transform);
      const zoomPercent = Math.round(event.transform.k * 100);
      d3.select(".zoom-scale").text(`${zoomPercent}%`);
    };

    const zoom = d3.zoom().scaleExtent([0.5, 5]).on("zoom", handleZoom);
    svg.call(zoom);
  }

  static setupSimulation(svg) {
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
  
  setNodes(nodes, state, drag) {
    this.node = this.node
      .data(nodes)
      .join("circle")
      .attr("r", (d) => d.config.size)
      .attr("fill", (d) => d.config.color)
      .call(drag)
      .on("click", (d) => {
        handleNodeClick(d, state);
      });
  }

  setLabels(nodes) {
    this.label = this.label
      .data(nodes)
      .join("text")
      .text((d) => d.name || "Unamed Node")
      .attr("dy", (d) => d.config.size * 1.5);
  }
}

function handleNodeClick(d, state) {
  if (d.ctrlKey || d.metaKey) {
    d3.select(this).classed("selected", 
      !d3.select(this).classed("selected")
    );
  } else {
    state.svg.selectAll(".selected").classed("selected", false);
    d3.select(this).classed("selected", true);
  }
}

/* 
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

  6. setup nodes 
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
        removed "selected" class from all other nodes 
      the node data would appear to the side
      would add all selected nodes 
  
  old way remaining steps 
    define title for the labels of the nodes

    define connections for the number of connections on 
    a node 


*/
