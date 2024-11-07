// ui_setup.js
import { Modal } from "../node-modal.js/guac-modal.js";
import { ConnectionModals } from "../node-modal.js/modal-assets.js";
import { ConnectionNode } from "./api_data.js";
export { SetupD3, GraphAssets };

/**
 * @class GraphAssets
 * @property {Object} edge - The edges of the graph.
 * @property {Object} node - The nodes of the graph.
 * @property {Object} label - The labels of the nodes.
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
	setNodes(dragFunc, context) {
		let { userSelection, nodes, nodeMap } = context;
		this.node = this.node
			.data(nodes)
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

		if (current.isRoot()) {
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
		if (first.identifier === "ROOT") {
			alert("Cannot view root node, select a different node.");
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
	/**
	 * when user zooms in or out
	 * the zoom level is updated
	 * @param {*} event
	 * @param {*} container
	 */
	static onZoom(event, container) {
		container.attr("transform", event.transform);
		const zoomPercent = Math.round(event.transform.k * 100);
		d3.select(".zoom-scale").text(`${zoomPercent}%`);
	}
}

class SetupD3 {
	/**
	 * finds the svg tag and appens the "g" tag
	 * which is the container for the entire topology
	 * @returns {Object} svg and container
	 */
	static initSVG() {
		const svg = d3.select("svg");
		const container = svg.append("g");
		SetupD3.setupZoom(svg, container);
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
					EventHandlers.onZoom(event, container);
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
