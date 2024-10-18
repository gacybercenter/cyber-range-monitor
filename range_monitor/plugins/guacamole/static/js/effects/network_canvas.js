// static/js/effects/network_canvas.js
export { NetworkCanvas };
// util funcs

/**
 * @param {string} justification - 'random', 'center', or 'corner'.
 * @param {number} width - Width of the canvas.
 * @param {number} height - Height of the canvas.
 * @returns {Point} - Instance of a subclass of Point.
 */
function createPoint(justification, width, height) {
  switch (justification.toLowerCase()) {
    case "random":
      return new RandomPoint(width, height);
    case "center":
      return new CenterPoint(width, height);
    case "corner":
    default:
      return new CornerPoint(width, height);
  }
}

/**
 * the dimensions required for a line between two points.
 * @param {Object} start - starting position with x and y properties.
 * @param {Object} end - ending position with x and y properties.
 * @returns {Object} - obj.length, obj.angle.
 */
function getLineDimensions(start, end) {
  const deltaX = end.x - start.x;
  const deltaY = end.y - start.y;

  const length = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
  const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI); // to degrees
  return { length, angle };
}

function createNode(size, justification) {
  const { width, height } = size;
  try {
    const point = createPoint(justification, width, height);
    const position = point.getPosition();

    const node = $('<div class="node"></div>').css({
      left: position.x + "px",
      top: position.y + "px",
    });

    return { $tag: node, position: position };
  } catch (error) {
    console.error(`NodeError: ${error}`);
    return null;
  }
}

/**
 * selects two distinct random nodes from the nodes array.
 * @param {Object[]} nodes - nodes[i].$tag, nodes[i].position.
 * @returns {Object} - Object containing start and end positions.
 */
function getNodePositions(nodes) {
  if (nodes.length < 2) {
    console.error("Not enough nodes to create a connection.");
    return null;
  }

  const startIndex = Math.floor(Math.random() * nodes.length);
  let endIndex = Math.floor(Math.random() * nodes.length);

  while (endIndex === startIndex) {
    endIndex = Math.floor(Math.random() * nodes.length);
  }

  return {
    start: nodes[startIndex].position,
    end: nodes[endIndex].position,
  };
}

/**
 * Retrieves the current size of the canvas.
 * @param {jQuery} $canvas - The jQuery element representing the canvas.
 * @returns {Object} - Object containing width and height.
 */
function getCanvasSize($canvas) {
  return {
    width: $canvas.width(),
    height: $canvas.height(),
  };
}
function findCanvas() {
  const $canvas = $("#networkCanvas");
  if ($canvas.length === 0) {
    throw new Error("NetworkCanvasError: Canvas element not found.");
  }
  return $canvas;
}

/**
 * Abstract Base Class representing a point with x and y coordinates.
 * Handles positioning logic based on justification.
 */
class Point {
  /**
   * creates a Point instance.
   * @param {number} width - the width of the canvas.
   * @param {number} height - the height of the canvas.
   */
  constructor(width, height) {
    if (new.target === Point) {
      throw new TypeError(
        "Cannot construct Point instances directly, use a subclass"
      );
    }
    this.x = 0;
    this.y = 0;
    this.setPositions(width, height);
  }

  /**
   * justifies the position by calculating x and y coordinates.
   * @param {number} width - The width of the canvas.
   * @param {number} height - The height of the canvas.
   */
  setPositions(width, height) {
    this.x = this.setAxis(width);
    this.y = this.setAxis(height);
  }

  /**
   * returns the x and y axis
   * @returns {Object} - (obj.x, obj.y).
   */
  getPosition() {
    return { x: this.x, y: this.y };
  }

  /**
   * sets the value of an axis using
   * 70% of the time.
   * @param {Number} dimension
   * @returns {Number}
   */
  setAxis(dimension) {
    if (Math.random() < 0.7) {
      return this.justifyAxis(dimension);
    } else {
      return Math.random() * dimension;
    }
  }
  /**
   * must be overridden by subclasses.
   * @param {Number} dimension
   * @returns {Number}
   */
  justifyAxis(dimension) {
    throw new Error("Must override justifyAxis method");
  }
}

/**
 * class representing a point placed randomly.
 */
class RandomPoint extends Point {
  /**
   * calculates a random point within the canvas.
   * no need to override justifyAxis.
   * @param {Number} dimension - width, height
   * @returns {Number} axis
   */
  setAxis(dimension) {
    return Math.random() * dimension;
  }
}

/**
 * @class CenterPoint(Point)
 */
class CenterPoint extends Point {
  /**
   * position biased towards the center of the canvas.
   * @param {Number} dimension
   * @returns {Number}
   */
  justifyAxis(dimension) {
    const center = dimension / 2;
    const margin = dimension * 0.4;
    return (Math.random() - 0.5) * margin + center;
  }
}
/**
 * @class CornerPoint(Point)
 */
class CornerPoint extends Point {
  /**
   * position biased towards the corners of the canvas.
   * @param {Number} dimension
   * @returns {Number}
   */
  justifyAxis(dimension) {
    const margin = dimension * 0.2;
    if (Math.random() < 0.5) {
      return Math.random() * margin; // top or left
    } else {
      return Math.random() * margin + dimension * 0.8; // bottom or right
    }
  }
}

/**
 * @class CanvasLine: represents a line animation on the canvas.
 * @property {Object} start - start.x, start.y
 * @property {jQuery} $line - represents the line
 * @property {Object} dimensions - dimensions.length, dimensions.angle
 *
 */
class CanvasLine {
  /**
   * @param {Object} start - start.x, start.y
   * @param {Object} end - end.x, end.y
   */
  constructor(start, end) {
    this.$line = $('<div class="line"></div>');
    this.dimensions = getLineDimensions(start, end);
  }
  /**
   * animates the line by expanding its width and then fading it out.
   */
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

  /**
   * applies CSS styles to the line based on its dimensions.
   * @param {Object} start - start.x, start.y
   */
  style(start) {
    this.$line.css({
      left: start.x + "px",
      top: start.y + "px",
      width: "10px",
      transform: `rotate(${this.dimensions.angle}deg)`,
    });
  }
}

/**
 * @class NetworkCanvas - holds state of the canvas.
 * @property {jQuery} $canvas - jQuery element representing the canvas.
 * @property {Object} settings - The settings for the canvas.
 * @property {Object} size - object w/ (size.width, size.height).
 * @property {Object[]} nodes - array of nodes objects (obj.$tag obj.position) .
 */
class NetworkCanvas {
  /**
   * Creates a NetworkCanvas instance.
   * @param {jQuery} $canvas - The jQuery element representing the canvas.
   */
  constructor($canvas) {
    this.$canvas = $canvas;
    this.settings = {
      nodeCount: 50,
      frequency: 1000,
      justifyNodes: "corner",
    };
    this.size = getCanvasSize(this.$canvas);
    this.nodes = [];
  }
  /**
   * draws the canvas and enables it
   */
  draw() {
    this.createNodes();
    this.animateConnections();
    $(window).on("resize", () => this.resizeCanvas());
  }

  /**
   * Creates nodes and appends them to the canvas.
   */
  createNodes() {
    for (let i = 0; i < this.settings.nodeCount; i++) {
      const nodeData = createNode(this.size, this.settings.justifyNodes);
      if (!nodeData) {
        continue;
      }
      this.$canvas.append(nodeData.$tag);
      this.nodes.push(nodeData);
    }
  }

  /**
   * Creates and animates a line between two points.
   * @param {Object} start - start.x, start.y
   * @param {Object} end - end.x, end.y
   */
  createLine(start, end) {
    const line = new CanvasLine(start, end);
    line.style(start);
    this.$canvas.append(line.$line);
    line.animate();
  }

  /**
   * continuously animates connections
   * between random nodes based on the frequency.
   */
  animateConnections() {
    const animate = () => {
      const positions = getNodePositions(this.nodes);

      if (!positions) return;

      this.createLine(positions.start, positions.end);
      const duration = this.settings.frequency + Math.random() * 200;
      setTimeout(animate, duration);
    };
    animate();
  }

  /**
   * repositions nodes & updates canvas size on window resize.
   */
  resizeCanvas() {
    this.size = getCanvasSize(this.$canvas);
    this.nodes.forEach((node) => {
      const point = createPoint(this.size.width, this.size.height);
      node.position = point.getPosition();
      node.$tag.css({
        left: node.position.x + "px",
        top: node.position.y + "px",
      });
    });
  }
  static disable() {
    const $canvas = findCanvas();
    $canvas.remove();
  }
  /**
   * finds the canvas tag "#networkCanvas"
   * @returns {jQuery} - The canvas element as a jQuery obj.
   */
  static find() {
    return findCanvas();
  }
}