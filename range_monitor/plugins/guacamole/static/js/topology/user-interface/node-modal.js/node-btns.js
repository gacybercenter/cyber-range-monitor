import { assetFactory } from "./template-assets";
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
  
  if(selectedIds.length > 1) {
    const timeline = buttonTemplates.createTimeline();
    timeline.disable("Timeline Not Available");
  }

  timeline.$tag.on("click", () => {
    buttonEvents.timelineClick(selectedIds, timeline);
  });
  
  nodeControls.push(timeline.$tag);
  return nodeControls;
}


export const buttonTemplates = {
  createTimeline() {
    const timeline = new NodeControl(
      "View Timeline (1)",
      { staticIcon: "fa-chart-line", hoverIcon: "fa-chart-bar" },
      "btn-timeline"
    );
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

function apiRequestTo(endpoint, data) {
  const apiEndpoint = `/guacamole/api/${endpoint}`;
  return $.ajax({
    url: apiEndpoint,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(data),
    dataType: "json",
  });
}



const buttonErrors = {
  apiError(message, buttonType, response) {
    alert(`${message}, check the console for more information.`);
    console.error(`${buttonType}Error[response]`, response);
  },
  xhrFailure(action, jqXHR, textStatus, errorThrown) {
    alert(`Failed to ${action} to the selected node(s), check the console for more information.`);
    console.error(`${action}Error[Status=${textStatus} | errorThrown=${errorThrown}]`, jqXHR);
  }
};

/**
 * button event handlers, all take selectedIds as a param
 * which is a string of node.identifiers
 */
export const buttonEvents = {
  /**
   * 
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectCntrl 
   */
  connectClick(selectedIds, connectCntrl) {
    const guacEndpoint = "connect-to-node";
    const apiData = JSON.stringify({ identifiers: selectedIds });
    connectCntrl.disable(`Connecting to ${selectedIds.length} node(s)...`);
    apiRequestTo(guacEndpoint, apiData)
      .done(function(response) {
        const { url, token } = response;
        if(!url || !token) {
          buttonErrors.apiError("The API did not respond with a URL or Token", "Connect", response);
          return;
        }
        const link = `${url}?token=${token}`;
        window.open(link, "_blank");
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        buttonErrors.xhrFailure("connect", jqXHR, textStatus, errorThrown);
      })
      .always(function() {
        connectCntrl.enable();
      });
  },
  /**
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectCntrl 
   */
  killClick(selectedIds, killCntrl) {
    const guacEndpoint = "kill-connections";
    const apiData = JSON.stringify({ identifiers: selectedIds });
    killCntrl.disable(`Killing ${selectedIds.length} node(s)...`);
    apiRequestTo(guacEndpoint, apiData)
      .done(function(response) {
        if (response.status !== "success") {
          buttonErrors.apiError("The API did not respond with a successful status code", "Kill", response);
          return;
        }
        alert(`Successfully killed ${selectedIds.length} node(s)`);
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
        buttonErrors.xhrFailure("kill", jqXHR, textStatus, errorThrown);
      })
      .always(function() {
        killCntrl.enable();
      });
  },
  /**
   * @param {string[]} selectedIds 
   * @param {NodeControl} connectCntrl 
   */
  timelineClick(selectedIds, timelineCntrl) {
    if(selectedIds.length !== 1) {
      alert("You can only view the timeline of one node at a time");
      return;
    } else if(selectedIds.length === 0) {
      alert("No nodes were selected to view the timeline of");
      return;
    }
    timelineCntrl.disable("Opening Timeline...");
    setTimeout(() => timelineCntrl.enable(), 1000);
    window.open(selectedIds[0] + "/connection_timeline", "_blank");
  },
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

