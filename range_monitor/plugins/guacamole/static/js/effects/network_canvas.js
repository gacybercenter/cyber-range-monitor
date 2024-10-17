/**
 * @class - Point
 * base class representing a point with
 * x and y coordinates.
 */
class Point {
  constructor() {
    if (new.target === Point) {
      throw new TypeError(
        "Cannot construct Point instances directly, use a subclass"
      );
    }
    this.x = 0;
    this.y = 0;
  }
  /**
   * justifies the content a point on the canvas
   * @param {number} width - the width of the canvas.
   * @param {number} height - the height of the canvas.
   */
  justify(width, height) {
    this.x = this.setAxis(width);
    this.y = this.setAxis(height);
    return { x: this.x, y: this.y };
  }

  /**
   * returns the value of an axis using
   * the justify to determine where position it
   * 70% of the time.
   * @param {Number} dimension
   * @returns {Number}
   */
  setAxis(dimension) {
    if (Math.random() < 0.7) {
      this.justifyAxis(dimension);
    } else {
      return Math.random() * dimension;
    }
  }
  justifyAxis(dimension) {
    return Math.random() * dimension;
  }
}

class RandomPoint extends Point {
  setAxis(dimension) {
    return Math.random() * dimension;
  }
}

class CenterPoint extends Point {
  justifyAxis(dimension) {
    const centerN = dimension / 2;
    const margin = dimension * 0.4;
    return (Math.random() - 0.5) * margin + centerN;
  }
}

class CornerPoint extends Point {
  /**
   * @returns {Object} - Object containing x and y coordinates.
   */
  justifyPoint(dimension) {
    const margin = dimension * 0.2;
    if (Math.random() < 0.5) {
      return Math.random() * margin; // top or left
    } else {
      return Math.random() * margin + dimension * 0.8; // right or bottom
    }
  }
}

/**
 * Factory function to create Point instances based on justification type.
 * @param {string} type - Justification type: 'random', 'center', or 'edge'.
 */
function createPoint(justification) {
  switch (justification.toLowerCase()) {
    case "center":
      return new CenterPoint();
    case "corner":
      return new CornerPoint();
    default:
    case "random":
      return new RandomPoint();
  }
}

/**
 * @param {Object} start - start.left, start.top 
 * @param {Object} end - end.left, end.top 
 * @returns {Number, Number} - obj.length, obj.angle
 */
function getLineDimensions(start, end) {
  const deltaX = end.left - start.left;
  const deltaY = end.top - start.top;

  const length = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI); // convert 2 degrees
  return { length, angle };
}
/**
 * after construction
 * - call create
 * - call animate
 * @class CanvasLine
 */
class CanvasLine {
  constructor(start, end) {
    this.$line = $('<div class="line"></div>');
    this.dimensions = {};
  }
  create(start, end) {
    this.dimensions = getLineDimensions(start, end);
    this.style();
    return this.$line;
  }
  animate() {
    this.$line.animate(
      { width: this.dimensions.length + "px" },
      {
        duration: 500 + Math.random() * 500,
        easing: "linear",
        complete: () => {
          setTimeout(() => {
            this.$line.fadeOut(200, function () {
              $(this).remove();
            });
          }, 100);
        },
      }
    );
  }
  // adds the css styles
  style() {
    this.$line.css({
      left: start.left + "px",
      top: start.top + "px",
      width: "0px",
      transform: `rotate(${this.dimensions.angle}deg)`,
    });
  }
}

class CanvasSettings {
  constructor(nodeCount = 50, frequency = 1000, justifyNodes = "corner") {
    this.nodeCount = nodeCount;
    this.frequency = frequency;
    this.justifyNodes = justifyNodes;
  }
  createPoint(justification) {
    switch (justification.toLowerCase()) {
      case "center":
        return new CenterPoint();
      case "corner":
        return new CornerPoint();
      default:
      case "random":
        return new RandomPoint();
    }
  }
}
/**
 *
 * @param {string} justify - 'center', 'edge', or 'random'
 * @param {Object} size - size.width, size.height
 * @returns
 */
function createNode(canvasSettings, size) {
  const { width, height } = size;
  try {
    const point = createPoint(canvasSettings.justifyNodes);
    const position = point.justify(width, height);

    const node = $('<div class="node"></div>').css({
      left: point.x + "px",
      top: point.y + "px",
    });
    return { $tag: node, position: position };
  } catch (error) {
    console.error(`NodeError: ${error}`);
  }
}
/**
 * @param {object[object]} nodes - array of node objects node.$tag, node.position(left, right)
 */
function getNodePositions(nodes) {
  const start = Math.floor(Math.random() * nodes.length);
  let end = Math.floor(Math.random() * nodes.length);

  while (end === start) {
    end = Math.floor(Math.random() * nodeCount);
  }
  return {
    start: nodes[start].position,
    end: nodes[end].position,
  };
}

function getCanvasSize($canvas) {
  return {
    width: $canvas.width(),
    height: $canvas.height(),
  };
}

/**
 * Class representing the network canvas.
 */
class NetworkCanvas {
  /**
   * Creates a NetworkCanvas instance.
   * @param {jQuery} canvas - The jQuery $tag representing the canvas.
   * @param {number} nodeCount - Number of nodes to create.
   * @param {number} frequency - Base frequency in milliseconds for line animations.
   * @param {string} justifyNodes - Justification type for node placement: 'edge', 'center', or 'random'.
   */
  constructor(canvas, settings) {
    this.$canvas = canvas;
    this.settings = settings;
    this.size = getCanvasSize(this.$canvas);
    this.nodes = [];
    this.init();
  }
  
 init() {
   this.createNodes();
   this.animateConnections();
   $(window).on("resize", () => this.onResize());
  }

  /**
   * Creates nodes and appends them to the canvas.
   */
  createNodes() {
    for (let i = 0; i < this.nodeCount; i++) {
      const nodeData = createNode(this.justifyNodes, this.size);
      this.$canvas.append(nodeData.$tag);
      this.nodes.push(nodeData);
    }
  }
  /**
   * creates and animates a line between two points.
   * @param {Object} start - start.left, start.top
   * @param {Object} end - end.left, end.top
   */
  createLine(start, end) {
    const line = new CanvasLine(start, end);
    const $line = line.create(start, end);
    this.$canvas.append($line);
    line.animate();
  }

  /**
   * animation loop for canvas note
  */
  animateConnections() {
    const animate = () => {

      if (this.nodes.length < 2) return;

      const { start, end } = getNodePositions(this.nodes);

      this.createLine(start, end);
      const duration = this.frequency + (Math.random() * 200);
      setTimeout(animate, duration);

    };
    animate();
  }

  /**
   * respositions node on resize for responsiveness
   */
  onResize() {
    this.size = getCanvasSize(this.$canvas);
    this.nodes.forEach((node) => {
      node = createNode(this.justifyNodes, this.size);
    });
  }
}

function exampleUsage() {
  const nodeCount = 50; // number of nodes
  const frequency = 1000; // base frequency in milliseconds
  const justifyNodes = "edge"; // 'edge', 'center', or 'random'
  const settings = new CanvasSettings(nodeCount, frequency, justifyNodes);

  const networkCanvasElement = $("#network-canvas");
  const networkCanvas = new NetworkCanvas(networkCanvasElement, settings);
}


