
/**
 * @param {string[]} selectedIds 
 * @param {boolean} includeTimeline
 * @returns {JQuery<HTMLButtonElement>[]}
 */
export function createNodeControls(selectedIds, includeTimeline = false) {
  const connect = buttonTemplates.createConnect();
  connect.$tag.on("click", () => {
    buttonEvents.connectClick(selectedIds);
  });
  
  const kill = buttonTemplates.createKill();
  kill.$tag.on("click", () => {
    buttonEvents.killClick(selectedIds);
  });

  const nodeControls = [
    connect,
    buttonTemplates.createKill(selectedIds)
  ];

  if (includeTimeline) {
    nodeControls.push(
      buttonTemplates.createTimeline(selectedIds)
    );
  }
  return nodeControls.map((cntrl) => cntrl.$tag);
}


export const buttonTemplates = {
  createTimeline(selectedIds) {
    const timeline = new NodeControl(
      "View Timeline (1)",
      { staticIcon: "fa-chart-line", hoverIcon: "fa-chart-bar" },
      "btn-timeline"
    );
    timeline.$tag.on("click", () => {
      buttonEvents.timelineClick(selectedIds);
    });
    return timeline;
  },
  createConnect() {
    const connect = new NodeControl(
      `Connect To Node(s)`,
      { staticIcon: "fa-plug", hoverIcon: "fa-wifi" },
      "btn-connect"
    );
    return connect;
  },
  createKill() {
    const kill = new NodeControl(
      `Kill Node(s)`,
      { staticIcon: "fa-smile", hoverIcon: "fa-skull-crossbones" },
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
  connectClick(selectedIds) {

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
    xhr.send(data);
  },
  killClick(selectedIds) {
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
    xhr.send(data);
    alert(`Killed ${selectedIds.length} connections`);
  },
  timelineClick(selectedIds) {
    if (selectedIds.length > 1) {
      alert("NOTE: Only the first selected nodes timeline will be displayed.");
    }
    window.open(selectedIds[0] + "/connection_timeline", "_blank");
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
 * @property {ControlIcons} cntrlIcons - the icons of the button
 * @property {string} btnClass - the css class of the button
 * @property {JQuery<HTMLButtonElement>} $tag - the button element
 * @method createHTML - creates the button element
 */
class NodeControl {
  constructor(btnText, cntrlIcons, btnClass) {
    this.text = btnText;
    this.cntrlIcons = cntrlIcons;
    this.btnClass = btnClass;
    this.$tag = this.createHTML();
  }
  /**
   * @returns {JQuery<HTMLButtonElement>}
   */
  createHTML() {
    const toggleIcon  = ($tag, remove, add) => {
      $tag
        .find("i")
        .removeClass(remove)
        .addClass(add);
    };
    
    const { staticIcon, hoverIcon } = this.cntrlIcons;
    this.$tag = $("<button>")
      .addClass("control-btn " + this.btnClass)
      .attr("aria-label", this.text)
      .html( `<i class="icon fas ${staticIcon}"></i> ${this.text}`)
      .hover(
        function () {
          toggleIcon($(this), staticIcon, hoverIcon);
        },
        function () {
          toggleIcon($(this), hoverIcon, staticIcon);
        }
      );
    return this.$tag;
  }
}

