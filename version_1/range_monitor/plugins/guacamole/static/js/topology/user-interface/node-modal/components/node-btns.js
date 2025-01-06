import { assetFactory } from "./template-assets.js";
export { NODE_CONTROLS, NodeControl, createAllControls, controlEvents };

const controlEvents = {
	/**
	 * @param {string} endpoint
	 * @returns {XMLHttpRequest}
	 */
	xhrRequestTo(endpoint) {
		const apiEndpoint = `/guacamole/api/${endpoint}`;
		const xhrGuac = new XMLHttpRequest();
		xhrGuac.open("POST", apiEndpoint, true);
		xhrGuac.setRequestHeader("Content-Type", "application/json");
		return xhrGuac;
	},
	/**
	 * @param {string[]} selectedIds
	 * @returns {void}
	 */
	connectToNodes(selectedIds) {
		const request = controlEvents.xhrRequestTo("connect-to-node");
		request.onreadystatechange = function () {
			if (
				request.readyState === XMLHttpRequest.DONE &&
				request.status === 200
			) {
				const response = JSON.parse(request.responseText);
				const link = `${response.url}?token=${response.token}`;
				window.open(link, "_blank");
			} else if (request.readyState === XMLHttpRequest.DONE) {
				alert(request.responseText);
			}
		};
		const data = JSON.stringify({ identifiers: selectedIds });
		request.send(data);
	},
	/**
	 * @param {string[]} selectedIds
	 * @returns {void}
	 */
	killNodes(selectedIds) {
		const request = controlEvents.xhrRequestTo("kill-connections");
		request.onreadystatechange = function () {
			if (request.readyState === XMLHttpRequest.DONE && request.status === 200) {
				const response = JSON.parse(request.responseText);
				console.log("Kill Button Response: ", response);
			} else if (request.readyState === XMLHttpRequest.DONE) {
				console.log("Kill Response", request.responseText);
			}
		};
		const data = JSON.stringify({ identifiers: selectedIds });
		request.send(data);
	},
	/**
	 * @param {string[]} selectedIds
	 * @returns {void}
	 */
	viewTimeline(selectedIds) {
		if (selectedIds.length > 1) {
			alert("NOTE: Only the first selected nodes timeline will be displayed.");
			return;
		}
		const connection = selectedIds[0];
		window.open(`${connection}/connection_timeline`, "_blank");
	},
};

/**
 * @typedef {Object} ControlOptions
 * @property {string} btnText
 * @property {Object} btnIcons - { staticIcon: string, hoverIcon: string }
 * @property {string} btnClass
 * @property {string} actionText
 */

const NODE_CONTROLS = Object.freeze({
	KILL: {
		btnText: "Kill Node(s)",
		btnIcons: {
			staticIcon: "fa-solid fa-face-smile",
			hoverIcon: "fa-solid fa-skull-crossbones",
		},
		btnClass: "btn-kill",
		actionText: "Killing Node(s)...",
	},
	CONNECT: {
		btnText: "Connect To Node(s)",
		btnIcons: {
			staticIcon: "fa-solid fa-plug",
			hoverIcon: "fa-solid fa-wifi",
		},
		btnClass: "btn-connect",
		actionText: "Connecting to Node(s)...",
	},
	TIMELINE: {
		btnText: "View Timeline (1)",
		btnIcons: {
			staticIcon: "fa-solid fa-chart-line",
			hoverIcon: "fa-solid fa-chart-bar",
		},
		btnClass: "btn-timeline",
		actionText: "Opening timeline in new tab...",
	},
});

/**
 * creates and binds the event listeners for all of the predefined
 * controls in NODE_CONTROLS and returns an array of the jquery object
 * of the buttons
 * @param {string[]} selectedIds - the identifiers of the selected nodes
 * @returns {JQuery<HTMLElement>[]} - array of buttons
 */
function createAllControls(selectedIds) {
	const controls = [
		new NodeControl(NODE_CONTROLS.CONNECT, () => {
			controlEvents.connectToNodes(selectedIds);
		}),
		new NodeControl(NODE_CONTROLS.KILL, () => {
			controlEvents.killNodes(selectedIds);
		}),
	];
	const timeline = new NodeControl(NODE_CONTROLS.TIMELINE);
	if (selectedIds.length !== 1) {
		timeline.disable("Timeline Unavailable");
		timeline.onClick("Error", () => timeline.errorAnimate());
	} else {
		timeline.onClick(NODE_CONTROLS.TIMELINE.actionText, () => {
			controlEvents.viewTimeline(selectedIds);
		});
	}
	controls.push(timeline);
	return controls.map((control) => control.$tag);
}

class NodeControl {
	static BUTTON_ERROR = "control-error";
	static BUTTON_OFF = "control-off";
	static BUTTON_TIMEOUT = 1500;

	/**
	 * @param {ControlOptions} controlOptions - { btnText[string], btnIcons, btnClass[string] }
	 * @param {function} eventHandler
	 */
	constructor(controlOptions, eventHandler = null) {
		const { btnText, btnIcons, btnClass, actionText } = controlOptions;
		this.btnIcons = btnIcons;
		this.$tag = assetFactory.createNodeBtn(btnText, btnClass, btnIcons);
		if (eventHandler) {
			this.onClick(actionText, eventHandler);
		}
	}
	disable(actionText) {
		this.$tag.addClass(NodeControl.BUTTON_OFF);
		this.setText(actionText);
	}

	/**
	 * does the harlem shake \ (•◡•) / (if an error occurs)
	 */
	errorAnimate() {
		this.$tag.addClass(NodeControl.BUTTON_ERROR);
		this.$tag.on("animationend", function () {
			$(this).removeClass(NodeControl.BUTTON_ERROR);
		});
	}
	isDisabled() {
		return this.$tag.hasClass(NodeControl.BUTTON_OFF);
	}
	setText(newText) {
		this.$tag.find(".node-btn-text").text(newText);
	}

	// old name -> addClickEvent

	/**
	 * handles toggling the UI of the button, the
	 * callback passed performs all else.
	 * @param {string} actionText - the string to display while action occurs
	 * @param {callback} callback - the event handler
	 */
	onClick(actionText, callback) {
		this.$tag.on("click", () => {
			if (this.isDisabled()) {
				this.errorAnimate();
				return;
			}
			const oldText = this.$tag.text();
			this.disable(actionText);
			callback(); // <- the users callback
			setTimeout(() => {
				this.$tag.removeClass(NodeControl.BUTTON_OFF);
				this.setText(oldText);
			}, NodeControl.BUTTON_TIMEOUT);
		});
	}
}
