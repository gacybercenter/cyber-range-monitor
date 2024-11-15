// add more modal controls here 
export { createNodeControls };

/**
 * @param {string[]} selectedIds - note u need to map 
 *  selectedIdentifiers to ids before calling the function
 * @param {boolean} includeTimeline
 * @returns {JQuery<HTMLButtonElement>[]}
 */
function createNodeControls(selectedIds, includeTimeline = false) {
  // .btn-connect
  console.log(selectedIds);
  
  const connect = new NodeControl(
    `Connect To Node(s)`,
    { staticIcon: "fa-plug", hoverIcon: "fa-wifi" },
    "btn-connect"
  );
  const kill = new NodeControl(
    `Kill Node(s)`,
    { staticIcon: "fa-smile", hoverIcon: "fa-skull-crossbones" },
    "btn-kill"
  );

  const controlObjs = [connect, kill];

  if (includeTimeline) {
    const timeline = new NodeControl(
      "View Timeline (1)",
      { staticIcon: "fa-chart-line", hoverIcon: "fa-chart-bar" },
      "btn-timeline"
    );
    
    timeline.$tag.on("click", () => {
      ButtonEvents.timelineClick(selectedIds);
    });

    controlObjs.push(timeline);
  }

  connect.$tag.on("click", () => {
    ButtonEvents.connectClick(selectedIds);
  });

  kill.$tag.on("click", () => {
    ButtonEvents.killClick(selectedIds);
  });
  return controlObjs.map((cntrl) => cntrl.$tag);
}

function xhrRequestTo(endpoint) {
  const apiEndpoint = `/guacamole/api/${endpoint}`;
  const xhrGuac = new XMLHttpRequest();
  xhrGuac.open("POST", apiEndpoint, true);
  xhrGuac.setRequestHeader("Content-Type", "application/json");
  return xhrGuac;
};

class ButtonEvents {
  /**
   * @param {string[]} selectedIds
   */
  static connectClick(selectedIds) {
    const xhr = xhrRequestTo("connect-to-node");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        const link = `${response.url}?token=${response.token}`;
        window.open(link, "_blank");
      } else if (xhr.readyState === XMLHttpRequest.DONE) {
        alert(xhr.responseText);
      } else if(xhr.status === 404) {
        alert("The connection endpoint does not exist")
      }
    };
    const data = JSON.stringify({ identifiers: selectedIds });
    xhr.send(data);
  }

  /**
   * TODO: maybe add alerts for the number of connections killed
   * @param {string[]} selectedIds
   */
  static killClick(selectedIds) {
    const xhr = xhrRequestTo("kill-connections");
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        console.log(response);
      } else if (xhr.readyState === XMLHttpRequest.DONE) {
        alert(xhr.responseText);
      }
    };
    const data = JSON.stringify({ identifiers: selectedIds });
    xhr.send(data);
    alert(`Killed ${selectedIds.length} connections`);
  }

  /**
   * @param {string[]} selectedIds
   */
  static timelineClick(selectedIds) {
    if (selectedIds.length > 1) {
      alert("NOTE: Only the first selected nodes timeline will be displayed.");
    }
    window.open(selectedIds[0] + "/connection_timeline", "_blank");
  }
}
/**
 * @typedef {Object} ControlIcons
 * @property {string} - staticIcon: the icon when it is not hovered
 * @property {string} - hoverIcon: the icon when it is hovered
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
    const { staticIcon, hoverIcon } = this.cntrlIcons;
    this.$tag = $("<button>")
      .addClass("control-btn " + this.btnClass)
      .attr("aria-label", this.text)
      .html( `
				<i class="icon fas ${staticIcon}"></i>	
				${this.text}
			`
      )
      .hover(
        function () {
          $(this)
            .find("i")
            .removeClass(staticIcon)
            .addClass(hoverIcon);
        },
        function () {
          $(this)
            .find("i")
            .removeClass(hoverIcon)
            .addClass(staticIcon);
        }
      );
    return this.$tag;
  }
}

