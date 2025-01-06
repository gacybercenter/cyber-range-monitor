// nw-node.js
import { Point } from "./point.js";

export const NodeStatus = Object.freeze({
  IDLE: "idle",
  ACTIVE: "active",
  SENDING: "sending",
});

/**
 * represents a single node in the network / graph.
 * @class
 * @property {number} id
 * @property {Point} position - the x, y of the node on the canvas.
 * @property {NodeStatus} status - current status of the node.
 * @property {JQuery<HTMLElement>} $element - the jQuery element representing the node in the dom.
 */
export class Node {
  /**
   * creates a new node instance.
   * @param {{ width: number, height: number }} size - the size of the canvas.
   * @param {string} justification - the justification strategy for positioning.
   * @param {number} id - unique identifier for the node.
   */
  constructor(size, justification, id) {
    this.id = id;
    this.position = Point.create(justification, size);
    this.status = NodeStatus.IDLE;
    this.$element = this.create();
  }

  /**
   * creates the jquery element for the node.
   * @returns {JQuery<HTMLElement>} the jquery node element.
   */
  create() {
    return $("<div>", { class: "node" })
      .css({
        left: `${this.position.x}px`,
        top: `${this.position.y}px`,
      })
      .attr("data-id", this.id);
  }

  /**
   * updates the status of the node and its corresponding css classes.
   * @param {string} status - the new status of the node.
   */
  updateStatus(status) {
    this.status = status;
    const oldStatus = Object.values(NodeStatus).join(" ");
    this.$element.removeClass(oldStatus).addClass(status);
  }

  /**
   * pulses the node a specified number of times with a given interval.
   * @param {number} [times=1] - number of pulses.
   * @param {number} [interval=300] - interval between pulses in milliseconds.
   * @returns {Promise<void>} resolves when pulsing is complete.
   */
  pulse(times = 1, interval = 300) {
    return new Promise((resolve) => {
      let count = 0;
      const doPulse = () => {
        if (count < times) {
          this.updateStatus(NodeStatus.ACTIVE);
          setTimeout(() => {
            this.updateStatus(NodeStatus.IDLE);
            count++;
            setTimeout(doPulse, interval);
          }, interval);
        } else {
          resolve();
        }
      };
      doPulse();
    });
  }

  /**
   * resizes the node by updating its position.
   * @param {Point} pos - the new position of the node.
   */
  resize(pos) {
    this.position = pos;
    this.$element.css({
      left: `${this.position.x}px`,
      top: `${this.position.y}px`,
    });
  }

  /**
   * creates a ripple effect on the node.
   */
  ripple() {
    const $ripple = $('<div class="ripple-effect"></div>');
    this.$element.append($ripple);
    setTimeout(() => $ripple.remove(), 1000);
  }

  /**
   * makes the node blink by toggling the 'blink' css class.
   */
  blink() {
    this.$element.addClass("blink");
    setTimeout(() => this.$element.removeClass("blink"), 1500);
  }
  equals(node) {
    return this.id === node.id;
  }
}
/**
 * manages a collection of node instances.
 * @class
 * @property {Node[]} nodes - array of node instances.
 * @property {number} count - total number of nodes.
 */
export class CanvasNodes {
  /**
   * creates a new CanvasNodes instance.
   * @param {{ width: number, height: number }} size - the size of the canvas.
   * @param {string} justification - the justification strategy for positioning.
   * @param {number} count - number of nodes to create.
   * @param {JQuery<HTMLElement>} $container - the container to append nodes to.
   */
  constructor(size, justification, count, $container) {
    this.nodes = [];
    this.count = count;
    this.createAll(size, justification, count, $container);
  }

  /**
   * creates and appends all nodes to the container.
   * @param {{ width: number, height: number }} size
   * @param {String} justification
   * @param {Number} count - number of nodes to create.
   * @param {JQuery<HTMLElement>} $container - the container to append nodes to.
   */
  createAll(size, justification, count, $container) {
    for (let i = 0; i < count; i++) {
      const node = new Node(size, justification, this.makeNodeId(count, i));
      this.nodes.push(node);
      $container.append(node.$element);
    }
  }

  /**
   * generates a unique node id based on index.
   * @param {Number} count - total number of nodes.
   * @param {Number} k - current index.
   * @returns {Number} the generated node id.
   */
  makeNodeId(count, k) {
    const primeNum = 33;
    return (k + (Math.pow(k, 2) % primeNum)) % count;
  }

  /**
   * finds a node that satisfies the given predicate.
   * @param {(node: Node) => boolean} predicate - the condition to match.
   * @returns {Node|undefined} the first matching node or undefined.
   */
  findBy(predicate) {
    return this.nodes.find(predicate);
  }

  /**
   * finds a node by its unique id.
   * @param {number} id - the id of the node.
   * @returns {Node|undefined} the matching node or undefined.
   */
  findById(id) {
    return this.findBy((node) => node.id === id);
  }

  /**
   * finds all nodes with the specified status.
   * @param {string} status - the status to filter by.
   * @returns {Node[]} array of nodes with the given status.
   */
  findByStatus(status) {
    return this.nodes.filter((node) => node.status === status);
  }

  /**
   * selects a random subset of nodes, excluding specified nodes.
   * @param {number} [count=1] - number of random nodes to select.
   * @param {Node[]} [exclusions=[]] - nodes to exclude from selection.
   * @returns {Node[]} array of randomly selected nodes.
   */
  selectRandom(count = 1, exclusions = []) {
    const availableNodes = this.nodes.filter(
      (node) => !exclusions.includes(node)
    );
    const randomized = availableNodes.sort(() => 0.5 - Math.random());
    return randomized.slice(0, count);
  }

  /**
   * makes all nodes blink.
   */
  blinkAll() {
    this.nodes.forEach((node) => node.blink());
  }

  /**
   * resizes all nodes based on the new size and justification.
   * @param {{ width: number, height: number }} size - the new size of the canvas.
   * @param {string} justification - the justification strategy for positioning.
   */
  resizeAll(size, justification) {
    this.nodes.forEach((node) => {
      const pos = Point.create(justification, size);
      node.resize(pos);
    });
  }

  /**
   * retrieves all nodes.
   * @returns {Node[]} - array of all nodes.
   */
  getAll() {
    return this.nodes;
  }
}
