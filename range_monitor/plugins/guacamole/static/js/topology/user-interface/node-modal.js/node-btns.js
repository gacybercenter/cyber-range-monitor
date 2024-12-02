import { assetFactory } from "./template-assets.js";
/**
 * @param {string[]} selectedIds 
 * @param {boolean} includeTimeline
 * @returns {JQuery<HTMLButtonElement>[]}
 */
export function createNodeControls(selectedIds) {
  const connect = buttonTemplates.createConnect();
  connect.$tag.on("click", () => {
    buttonEvents.connectClick(selectedIds, connect);
  });
  const kill = buttonTemplates.createKill();
  kill.$tag.on("click", () => {
    buttonEvents.killClick(selectedIds, kill);
  });
  const nodeControls = [
    connect.$tag,
    kill.$tag,
  ];
  
  const timeline = buttonTemplates.createTimeline();
  if(selectedIds.length > 1) {
    timeline.disable("Timeline Not Available");
  } else {
    timeline.$tag.on("click", () => {
      buttonEvents.timelineClick(selectedIds, timeline);
    });
  }
  nodeControls.push(timeline.$tag);
  return nodeControls;
}


export const buttonTemplates = {
  createTimeline() {
    const timeline = new NodeControl(
      "View Timeline (1)",
      { staticIcon: "fa-solid fa-chart-line", hoverIcon: "fa-solid fa-chart-bar" },
      "btn-timeline"
    );
    return timeline;
  },
  createConnect() {
    const connect = new NodeControl(
      `Connect To Node(s)`,
      { staticIcon: "fa-solid fa-plug", hoverIcon: "fa-solid fa-wifi" },
      "btn-connect"
    );
    return connect;
  },
  createKill() {
    const kill = new NodeControl(
      `Kill Node(s)`,
      { staticIcon: "fa-solid fa-face-smile", hoverIcon: "fa-solid fa-skull-crossbones" },
      "btn-kill"
    );
    return kill;
  }
};

/**
 * button event handlers, all take selectedIds as a param
 * which is a string of node.identifiers
 */
export const buttonEvents = {
  connectClick(selectedIds, connectBtn) {
    
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
    setTimeout(() => {
      connectBtn.enable();
    }, 1000);
  },
  killClick(selectedIds, killBtn) {
    const xhr = this.xhrRequestTo("kill-connections");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        console.log("Kill Click Response: ", response)
      } else if (xhr.readyState === XMLHttpRequest.DONE) {
        alert(xhr.responseText);
      }
    };
    const data = JSON.stringify({ identifiers: selectedIds });
    killBtn.disable("Killing...");
    xhr.send(data);
    setTimeout(() => {
      killBtn.enable();
    }, 1000);
    alert(`Killed ${selectedIds.length} connections`);
  },
  timelineClick(selectedIds, timelineBtn) {
    if (selectedIds.length > 1) {
      alert("NOTE: Only the first selected nodes timeline will be displayed.");
      return;
    }
    timelineBtn.disable("Loading Timeline...");
    window.open(selectedIds[0] + "/connection_timeline", "_blank");
    setTimeout(() => {
      timelineBtn.enable();
    });
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
  }
};


/**
 * @typedef {Object} ControlIcons
 * @property {string} - staticIcon: fas  icon when it is not hovered
 * @property {string} - hoverIcon: fas icon when it is hovered
*/
/**
 * @class NodeControl
 * @property {string} text - the text of the button
 * @property {ControlIcons} btnIcons - the icons of the button
 * @property {string} btnClass - the css class of the button
 * @property {JQuery<HTMLButtonElement>} $tag - the button element
 * @method createHTML - creates the button element
 */
class NodeControl {
  constructor(btnText, btnIcons, btnClass) {
    this.text = btnText;
    this.btnIcons = btnIcons;
    this.btnClass = btnClass;
    this.$tag = assetFactory.createNodeBtn(btnText, btnClass, btnIcons);
  }
  /**
   * prevents the button from being clicked while sending ajax request
   * @param {string} btnText - the text while btn is disabled 
   */
  disable(inProgressText) {
    this.$tag.prop("disabled", true).css({
      "cursor": "not-allowed",
      "opacity": "0.5"
    });
    this.textTag.text(inProgressText);
  }
  /**
   * enables the button after ajax request is complete
   */
  enable() {
    this.$tag.prop("disabled", false).css({
      "cursor": "pointer",
      "opacity": "1"
    });
    this.textTag.text(this.text);
  }
  get textTag() {
    return this.$tag.find(".node-btn-text");
  }
}

