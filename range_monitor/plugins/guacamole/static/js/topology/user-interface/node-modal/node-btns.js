import { assetFactory } from "./template-assets.js";
/**
 * @param {string[]} selectedIds
 * @param {boolean} includeTimeline
 * @returns {JQuery<HTMLButtonElement>[]}
 */

/**
 * @typedef {Object} ControlIcons
 * @property {string} - staticIcon: fas  icon when it is not hovered
 * @property {string} - hoverIcon: fas icon when it is hovered
 */

/**
 * @enum {Object}
 * font awesome icon classes
 */
const buttonConfig = {
	connect: {
		staticIcon: "fa-solid fa-plug",
		hoverIcon: "fa-solid fa-wifi",
	},
	kill: {
		staticIcon: "fa-solid fa-face-smile",
		hoverIcon: "fa-solid fa-skull-crossbones",
	},
	timeline: {
		staticIcon: "fa-solid fa-chart-line",
		hoverIcon: "fa-solid fa-chart-bar",
	},
  buttonTimeout: 1500,
  btnText: ".node-btn-text",
  btnOff: "control-off",
  btnError: "control-error",
};

export function createNodeControls(selectedIds) {
	const connect = buttonTemplates.createConnect();
	connect.$tag.on("click", () => {
		buttonEvents.connectClick(selectedIds, connect);
	});
	const kill = buttonTemplates.createKill();
	kill.$tag.on("click", () => {
		buttonEvents.killClick(selectedIds, kill);
	});
	const nodeControls = [connect.$tag, kill.$tag];

	const timeline = buttonTemplates.createTimeline();
	if (selectedIds.length > 1) {
		timeline.disable("Timeline Not Available");
	} else {
		timeline.$tag.on("click", () => {
			buttonEvents.timelineClick(selectedIds, timeline);
		});
	}
	nodeControls.push(timeline.$tag);
	return nodeControls;
}

/**
 * creates the node control objects
 */
export const buttonTemplates = {
	createTimeline() {
		const { staticIcon, hoverIcon } = buttonConfig.timeline;
		const timeline = new NodeControl(
			"View Timeline (1)",
			{
				staticIcon: staticIcon,
				hoverIcon: hoverIcon,
			},
			"btn-timeline"
		);
		return timeline;
	},
	createConnect() {
		const { staticIcon, hoverIcon } = buttonConfig.connect;
		const connect = new NodeControl(
			`Connect To Node(s)`,
			{
				staticIcon: staticIcon,
				hoverIcon: hoverIcon,
			},
			"btn-connect"
		);
		return connect;
	},
	createKill() {
		const { staticIcon, hoverIcon } = buttonConfig.kill;
		const kill = new NodeControl(
			`Kill Node(s)`,
			{
				staticIcon: staticIcon,
				hoverIcon: hoverIcon,
			},
			"btn-kill"
		);
		return kill;
	},
};

/**
 * button event handlers, all take selectedIds as a param
 * which is a string of node identifiers;
 *
 * NOTE
 * i opted not to use jQuery AJAX here, because I assume
 * that in the future we will phase out using jQuery
 */
export const buttonEvents = {
  /**
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectBtn 
   * @returns {void}
   */  
	connectClick(selectedIds, connectBtn) {
		if (connectBtn.isDisabled()) {
			connectBtn.errorAnimate();
			return;
		}
		const xhr = this.xhrRequestTo("connect-to-node");
		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
				const response = JSON.parse(xhr.responseText);
				const link = `${response.url}?token=${response.token}`;
				window.open(link, "_blank");
			} else if (xhr.readyState === XMLHttpRequest.DONE) {
				alert(xhr.responseText);
			}
		};
		const data = JSON.stringify({ identifiers: selectedIds });
		connectBtn.disable("Connecting...");
		xhr.send(data);
		setTimeout(() => connectBtn.enable(), buttonConfig.buttonTimeout);
	},
  /**
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectBtn 
   * @returns {void}
   */
	killClick(selectedIds, killBtn) {
		if (killBtn.isDisabled()) {
			connectBtn.errorAnimate();
			return;
		}
		const xhr = this.xhrRequestTo("kill-connections");
		xhr.onreadystatechange = function () {
			if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
				const response = JSON.parse(xhr.responseText);
				console.log("Kill Button Response: ", response);
			} else if (xhr.readyState === XMLHttpRequest.DONE) {
				alert(xhr.responseText);
			}
		};
		const data = JSON.stringify({ identifiers: selectedIds });
		killBtn.disable("Killing...");
		xhr.send(data);
		setTimeout(() => killBtn.enable(), buttonConfig.buttonTimeout);
		alert(`Killed ${selectedIds.length} connections`);
	},
  /**
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectBtn 
   * @returns {void}
   */
	timelineClick(selectedIds, timelineBtn) {
		if (timelineBtn.isDisabled()) {
			connectBtn.errorAnimate();
			return;
		}
		if (selectedIds.length > 1) {
			alert("NOTE: Only the first selected nodes timeline will be displayed.");
			return;
		}
		timelineBtn.disable("Loading Timeline...");
		window.open(selectedIds[0] + "/connection_timeline", "_blank");
		setTimeout(() => timelineBtn.enable(), buttonConfig.buttonTimeout);
	},
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
};

/**
 * @class NodeControl
 * @property {string} text - the text of the button
 * @property {ControlIcons} btnIcons - the icons of the button
 * @property {string} btnClass - the css class of the button
 * @property {JQuery<HTMLButtonElement>} $tag - the button element
 * @method createHTML - creates the button element
 */
class NodeControl {
  /**
   * @param {string} btnText 
   * @param {ControlIcons} btnIcons 
   * @param {string} btnClass 
   */
	constructor(btnText, btnIcons, btnClass) {
		this.text = btnText;
		this.btnIcons = btnIcons;
		this.btnClass = btnClass;
		this.$tag = assetFactory.createNodeBtn(btnText, btnClass, btnIcons);
	}
	/**
	 * prevents the button from being clicked while sending an ajax request
	 * to stop user from sending multiple requests at once.
	 * @param {string} btnText - the text while btn is disabled
	 * @returns {void}
	 */
	disable(inProgressText) {
		this.$tag.addClass(buttonConfig.btnOff);
		this.btnText.text(inProgressText);
	}
	/**
	 * enables the button after ajax request is complete
	 * @returns {void}
	 */
	enable() {
		this.$tag.removeClass(buttonConfig.btnOff);
		this.btnText.text(this.text);
	}
	/**
	 * @returns {void}
	 */
	errorAnimate() {
		this.$tag.addClass(buttonConfig.btnError);
		this.$tag.on("animationend", function() {
			$(this).removeClass(buttonConfig.btnError);
		});
	}
	/**
	 * @returns {boolean}
	 */
	isDisabled() {
		return this.$tag.hasClass(buttonConfig.btnOff);
	}
	/**
	 * @returns {JQuery<HTMLElement>}
	 */
	get btnText() {
		return this.$tag.find(buttonConfig.btnText);
	}
}
