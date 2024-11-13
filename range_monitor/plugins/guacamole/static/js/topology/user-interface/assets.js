// ui_setup.js
import { Modal } from "./node-modal.js/guac-modal.js";
import { ConnectionModals } from "./node-modal.js/modal-assets.js";

export { setupD3, GraphAssets };

/**
 * @class GraphAssets
 * @property {Object} edge - The edges of the graph.
 * @property {Object} node - The nodes of the graph.
 * @property {Object} label - The labels of the nodes.
 */
class GraphAssets {
	constructor(svg) {
		this.edge = svg
			.append("g")
			.attr("id", "edge-container")
			.attr("stroke-width", 1)
			.selectAll("line");
		this.node = svg.append("g")
		.attr("id", "node-container")
		.selectAll("circle");
		this.label = svg
			.append("g")
			.attr("pointer-events", "none")
			.attr("text-anchor", "middle") 
			.selectAll("text");
			
		this.icon = svg
			.append("g")
			.attr("id", "icon-container")
			.classed("node-icon", true)
			.selectAll("text");
	}

	createLinks(edgeData, nodeMap) {
  	this.edge = this.edge.data(edgeData, (d) => `${d.source}-${d.target}`)
			.join("line")
  	  .attr("class", (d) => {
				const target = nodeMap.get(d.target);
  	    const status = target.isActive() ? "active-edge" : "inactive-edge";
  	    return `graph-edge ${status}`;
  	  })
  	  .attr("data-parent-id", d => d.source)
  	  .attr("data-target-id", d => d.target);
	}


	/**
	 *
	 * @param {*} dataNodes
	 * @param {*} dragFunc
	 * @param {Object{}} context
	 */
	setNodes(dragFunc, context) {
		let { userSelection, nodes, nodeMap } = context;

		this.node = this.node.data(nodes, (d) => d.identifier).join("circle")
			.attr("data-parent-id", (d) => d.parentIdentifier ?? "None")
			.attr("id", (d) => d.identifier)
			.attr("class", (d) => `${d.cssClass} graph-node`)
			.attr("r", (d) => d.size)
			.attr("fill", (d) => d.color)
			.call(dragFunc)
			.on("click", function (event) {
				event.preventDefault();
				eventHandlers.nodeClick(event, userSelection);
			})
			.on("auxclick", (event) => {
				event.preventDefault();
				eventHandlers.showNodeModal(userSelection, nodes, nodeMap);
			})
			.on("mouseenter", (event) => {
				eventHandlers.onNodeHover(event);
			})
			.on("mouseleave", () => {
				eventHandlers.onNodeHoverEnd();
			});
	}
	setIcons(dataNodes) {
		this.icon = this.icon.data(dataNodes, (d) => `icon-${d.identifier}`)
			.join("text")
			.text((d) => d.icon)
			.attr("dy", d => d.size / 6)
			.attr("pointer-events", "none")
			.attr("text-anchor", "middle")
			.attr("dominant-baseline", "middle")
			.style("font-size", (d) => d.size + "px");
	}

	setLabels(dataNodes) {
		this.label = this.label.data(dataNodes, (d) => `label-${d.identifier}`)
			.join("text")
			.text((d) => d.name || "Unamed Node")
			.attr("font-size", (d) => d.size + "px")
			.attr("dy", (d) => d.size + 5)
			.attr("class", (d) => (d.isActive() ? "active-label" : "inactive-label"));
	}

	/**
	 * logic for when the simulation ticks
	 */
	onTick() {
		this.edge
			.attr("x1", d => d.source.x)
			.attr("y1", d => d.source.y)
			.attr("x2", d => d.target.x)
			.attr("y2", d => d.target.y);
		this.node
			.attr("cx", (d) => d.x)
			.attr("cy", (d) => d.y);
		this.label
			.attr("x", (d) => d.x)
			.attr("y", (d) => d.y);
		this.icon
			.attr("x", (d) => d.x)
			.attr("y", (d) => d.y);
	}
}

const eventHandlers  = {
	/**
	 * @param {*} event
	 * @param {ConnectionNode>} userSelection
	 * @returns {void}
	 */
	nodeClick(event, userSelection) {
		const targetData = event.target.__data__;
		if(targetData.isRoot()) {
			return;
		}
		const isGroupSelect = event.ctrlKey || event.metaKey; 
		const $pressed = $(event.target);
		const selectedNodes = new Set(userSelection);
		if(!isGroupSelect || targetData.isGroup()) {
			$(".selected").each(function() {
				const targetId = $(this).attr("id");
				$(`line[data-target-id="${targetId}"]`)
					.removeClass("pressed-edge");
				$(this).removeClass("selected");	
			});
			selectedNodes.clear();
			if(!$pressed.hasClass("selected")) {
				$pressed.addClass("selected");
				$(`line[data-target-id="${targetData.identifier}"]`)
					.addClass("pressed-edge");
				selectedNodes.add(targetData);
			}
		} else {
			$pressed.toggleClass("selected");
			if(selectedNodes.has(targetData)) {
				selectedNodes.delete(targetData);
				$(`line[data-target-id="${targetData.identifier}"]`)
					.removeClass("pressed-edge");
			} else {
				selectedNodes.add(targetData);
				$(`line[data-target-id="${targetData.identifier}"]`)
					.addClass("pressed-edge");
			}
		}
		userSelection.length = 0;
		userSelection.push(...selectedNodes);
	},

	/**
	 * triggers on middle click
	 * @param {Set<string>} userSelection
	 * @param {ConnectionNode[]} nodes
	 * @param {Map<string, ConnectionNode>} nodeMap
	 */
	showNodeModal(userSelection, nodes, nodeMap) {
		if(userSelection.length === 0) return;

		const modal = new Modal();
		let modalData, title;
		let icon = null;
		const first = userSelection[0];
		// ^- add better safety 

		if (first.identifier === "ROOT") {
			alert("Cannot view root node, select a different node.");
			return;
		} else if (first.isGroup()) {
			modalData = ConnectionModals.connectionGroup(first, nodes, nodeMap);
			title = `Connection Group: ${first.name} `;
		} else if (userSelection.length === 1) {
			modalData = ConnectionModals.singleConnection(first, nodeMap);
			title = `Connection Details: ${first.name} `;
		} else {
			modalData = ConnectionModals.manyConnections(userSelection, nodeMap);
			title = `Selected Connections Overview (${userSelection.length}) `;
			icon = $(`<i class="fa-solid fa-users-viewfinder"></i>`);
		}
		modal.init(title, modalData);
		const $title = $("#modalTitle");
		if(!icon) {
			icon = first.getOsIcon();
		}
		$title.append(icon);
		modal.openModal();
	},
	/**
	 * when user zooms in or out
	 * the zoom level is updated
	 * @param {*} event
	 * @param {*} container
	 */
  onZoom(event, container) {
		container.attr("transform", event.transform);
		const zoomPercent = Math.round(event.transform.k * 100);
		d3.select(".zoom-scale").text(`${zoomPercent}%`);
	},
	onNodeHover(event) {
		const targetData = event.target.__data__;
		if(!targetData.isLeafNode()) {
			return;
		}
		$(`line[data-target-id="${targetData.identifier}"]`)
			.addClass("glow-effect");
		
		$(`#${targetData.identifier}`)
			.addClass("glow-circle");
	},
	onNodeHoverEnd() {
		$(".glow-effect").removeClass("glow-effect");
		$(".glow-circle").removeClass("glow-circle");
	}
}

const setupD3 = {
	initSVG() {
		const svg = d3.select("svg");
		const container = svg.append("g");
		this.setupZoom(svg, container);
		return { svg, container };
	},
	setupZoom(svg, container) {
		svg.call(
			d3.zoom().scaleExtent([0.5, 5])
			.on("zoom", (event) => {
				eventHandlers.onZoom(event, container);
			})
		);
	},
	setupSimulation(svg) {
		const { width, height } = svg.node().getBoundingClientRect();
		// change as needed 
		const SIM_CONFIG = {
			DISTANCE: 200,
			CHARGE: -400,
			ALPHA_DECAY: 0.05,
			VELOCITY_DECAY: 0.3,
		};

		return d3
			.forceSimulation()
			.force(
				"link",
				d3.forceLink()
					.id((d) => d.identifier)
					.distance(SIM_CONFIG.DISTANCE) // pull a link has
			)
			.force(
				"charge",
				d3.forceManyBody()
					.strength(SIM_CONFIG.CHARGE) // charge of each node
			)
			.force(
				"center", d3.forceCenter(width / 2, height / 2)
			)
			.force(
				"collision",
				d3.forceCollide()
					.radius((d) => d.size + 10) // collision raidus 
			)
			// .alphaDecay(SIM_CONFIG.ALPHA_DECAY) // alpha decay
      // .velocityDecay(SIM_CONFIG.VELOCITY_DECAY); // velocity decay
	},
	setupFilters(svg) {
		const defs = svg.append("defs");
		const filter = defs.append("filter").attr("id", "glow");
		filter
			.append("feGaussianBlur")
			.attr("class", "blur")
			.attr("stdDeviation", 4)
			.attr("result", "coloredBlur");

		const feMerge = filter.append("feMerge");

		feMerge.append("feMergeNode").attr("in", "coloredBlur");
		feMerge.append("feMergeNode").attr("in", "SourceGraphic");
	}
}
