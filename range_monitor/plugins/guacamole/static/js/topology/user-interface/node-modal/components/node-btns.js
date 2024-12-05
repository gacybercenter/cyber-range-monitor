import { assetFactory } from "./template-assets.js";
export { createNodeControls, buttonEvents, buttonTemplates };


/**
 * @enum {Object}
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
  buttonTimeout: 1500, // how to disable 
  btnText: ".node-btn-text",
  btnOff: "control-off",
  btnError: "control-error",
};

function createNodeControls(selectedIds) {
	const connect = buttonTemplates.createConnect();
	connect.addClickEvent(() => {
		buttonEvents.connectClick(selectedIds, connect);
	});
	const kill = buttonTemplates.createKill();
	kill.addClickEvent(() => {
		buttonEvents.killClick(selectedIds, kill);
	});
	const nodeControls = [connect.$tag, kill.$tag];

	const timeline = buttonTemplates.createTimeline();
	if (selectedIds.length > 1) {
		timeline.disable("Timeline Not Available");
	} else {
		timeline.addClickEvent(() => {
			buttonEvents.timelineClick(selectedIds, timeline);
		});
	}
	nodeControls.push(timeline.$tag);
	return nodeControls;
}

const buttonTemplates = {
	createTimeline: () => {
		return new NodeControl(
			"View Timeline (1)", buttonConfig.timeline, "btn-timeline"
		);
	},
	createConnect: () => {
		return new NodeControl(
			"Connect To Node(s)", buttonConfig.connect, "btn-connect"
		);
	},
	createKill: () => {
		return new NodeControl(
			"Kill Node(s)", buttonConfig.kill, "btn-kill"
		);
	},
};

/** NOTE -v
 * i opted NOT to use jQuery AJAX here, because I assume
 * that in the future we will phase out using jQuery
 */
const buttonEvents = {
  /**
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectBtn 
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
   * @param {NodeControl} killBtn 
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
				console.log("Kill Response", xhr.responseText);
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
   * @param {NodeControl} timelineBtn 
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

class NodeControl {
  /**
   * @param {string} btnText 
   * @param {Object} btnIcons - { staticIcon: string, hoverIcon: string } 
   * @param {string} btnClass 
   */
	constructor(btnText, btnIcons, btnClass) {
		this.text = btnText;
		this.btnIcons = btnIcons;
		this.btnClass = btnClass;
		this.$tag = assetFactory.createNodeBtn(btnText, btnClass, btnIcons);
	}
	/**
	 * prevents the button from sending multiple requests at once.
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
	 * does the harlem shake \ (•◡•) /
	 * if an error occurs
	 */
	errorAnimate() {
		this.$tag.addClass(buttonConfig.btnError);
		this.$tag.on("animationend", function() {
			$(this).removeClass(buttonConfig.btnError);
		});
	}
	isDisabled() {
		return this.$tag.hasClass(buttonConfig.btnOff);
	}
	get btnText() {
		return this.$tag.find(buttonConfig.btnText);
	}
	addClickEvent(callback) {
		this.$tag.on("click", callback);
	}
}
