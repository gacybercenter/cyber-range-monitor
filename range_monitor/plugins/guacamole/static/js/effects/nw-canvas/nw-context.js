// nw-canvas/nw-context.js
import { Node } from "./nw-node.js";

/**
 * represents the graph structure of nodes and their connections.
 * @class
 * @property {Node[]} nodes - array of node instances.
 * @property {Map<number, { node: number, weight: number }[]>} adjacencyList
 */
export class Graph {
  /**
   * creates a new Graph instance.
   * @param {Node[]} nodes - array of node instances.
   */
  constructor(nodes) {
    this.nodes = nodes;
    this.adjacencyList = new Map();
  }

  /**
   * builds the adjacency list for the graph based on node positions.
   */
  build() {
    this.nodes.forEach((node) => {
      this.adjacencyList.set(node.id, []);
    });
    const makeVertex = (id, weight) => ({ node: id, weight });
    for (let i = 0; i < this.nodes.length; i++) {
      for (let j = i + 1; j < this.nodes.length; j++) {
        const nodeA = this.nodes[i];
        const nodeB = this.nodes[j];
        const distance = this.getDistance(nodeA.position, nodeB.position);
        this.adjacencyList.get(nodeA.id).push(makeVertex(nodeB.id, distance));
        this.adjacencyList.get(nodeB.id).push(makeVertex(nodeA.id, distance));
      }
    }
  }

  /**
   * calculates the euclidean distance between two points.
   * @param {Point} posA - the first point.
   * @param {Point} posB - the second point.
   * @returns {number} the distance between posA and posB.
   */
  getDistance(posA, posB) {
    const dX = posB.x - posA.x;
    const dY = posB.y - posA.y;
    return Math.sqrt(dX * dX + dY * dY);
  }

  /**
   * finds the shortest path between two nodes using dijkstra's algorithm.
   * @param {number} startId - the id of the start node.
   * @param {number} endId - the id of the end node.
   * @returns {number[]} array of node ids representing the shortest path.
   */
  shortestPath(startId, endId) {
    const distances = new Map();
    const previous = new Map();
    const queue = new Set();

    this.nodes.forEach((node) => {
      distances.set(node.id, Infinity);
      previous.set(node.id, null);
      queue.add(node.id);
    });

    distances.set(startId, 0);

    while (queue.size > 0) {
      let current = null;
      let smallest = Infinity;
      queue.forEach((nodeId) => {
        const dist = distances.get(nodeId);
        if (dist < smallest) {
          smallest = dist;
          current = nodeId;
        }
      });

      if (current === endId || smallest === Infinity) {
        break;
      }

      queue.delete(current);

      this.adjacencyList.get(current).forEach((neighbor) => {
        if (!queue.has(neighbor.node)) {
          return;
        }
        const alt = distances.get(current) + neighbor.weight;
        if (alt < distances.get(neighbor.node)) {
          distances.set(neighbor.node, alt);
          previous.set(neighbor.node, current);
        }
      });
    }

    const path = [];
    let current = endId;
    while (current !== null) {
      path.unshift(current);
      current = previous.get(current);
    }
    const resultsFound = distances.get(endId) !== Infinity;
    return resultsFound ? path : [];
  }
}
