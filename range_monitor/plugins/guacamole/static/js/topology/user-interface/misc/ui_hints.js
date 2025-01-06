// topology/user-interface/ui_hints.js
export { NavigationHints, LoadScreen };

/**
 * @class NavigationHints
 * @description
 * displays the controls to the user
 * and highlights keys when they are pressed
 */
class NavigationHints {
  static hints = [
    {
      about: "To navigate the topology and drag nodes",
      keys: ["Click", "Drag"],
    },
    {
      about: "To zoom in and out of the topology",
      keys: ["Scroll"],
    },
    {
      about: "Double click to zoom in",
      keys: ["Double Click"],
    },
    {
      about: "To select multiple nodes at once",
      keys: ["Ctrl", "Click"],
    },
    {
      about: "To control all selected nodes",
      keys: ["Ctrl", "Alt"],
    },
    {
      about: "On a node to access controls and connection information",
      keys: ["Middle Click"],
    },
  ];
  static keyMap = {
    CTRL: "Ctrl",
    ALT: "Alt",
    SHIFT: "Shift",
    COMMAND: "Cmd",
    META: "Cmd", // For Mac users
    CLICK: "Click",
    "DOUBLE CLICK": "Double Click",
    "MIDDLE CLICK": "Middle Click",
    SCROLL: "Scroll",
    DRAG: "Drag",
    DROP: "Drop",
  };

  static init() {
    this.renderHints();
    this.setupToggleButton();
    this.setupEventListeners();
  }

  static renderHints() {
    const container = d3.select("#nav-hints");

    const navHints = container
      .selectAll(".nav-hint")
      .data(this.hints)
      .enter()
      .append("div")
      .attr("class", "nav-hint");

    navHints.each(function (d) {
      const hint = d3.select(this);

      d.keys.forEach((key, index) => {
        const isModifier = ["Ctrl", "Alt", "Shift", "Cmd"].includes(key);
        hint
          .append("span")
          .attr("class", isModifier ? "key modifier" : "key")
          .text(NavigationHints.formatKey(key));

        if (d.keys.length > 1 && index < d.keys.length - 1) {
          hint.append("span").attr("class", "plus-sign").text("+");
        }
      });

      hint.append("span").attr("class", "description").text(d.about);
    });
  }
  static formatKey(key) {
    const upperKey = key.toUpperCase();
    return (
      this.keyMap[upperKey] || (key.length === 1 ? key.toUpperCase() : key)
    );
  }
  static highlightKeys(keyLabel) {
    const keys = d3.selectAll(".key").filter(function () {
      return d3.select(this).text() === keyLabel;
    });

    keys.classed("highlighted", true);

    setTimeout(() => {
      keys.classed("highlighted", false);
    }, 200);
  }

  static setupToggleButton() {
    const toggleButton = d3.select("#hideHints");
    const navHintsContainer = d3.select("#nav-hints");

    toggleButton.on("click", () => {
      const isHidden = navHintsContainer.classed("hidden");
      navHintsContainer.classed("hidden", !isHidden);
      toggleButton.classed("rotated", !isHidden);
    });
  }

  static setupEventListeners() {
    document.addEventListener("keydown", (event) => {
      const keysPressed = this.getKeysPressed(event);
      keysPressed.forEach((key) => {
        this.highlightKeys(key);
      });
    });

    $(document).on("click", () => {
      this.highlightKeys("Click");
    });

    $(document).on("dblclick", () => {
      this.highlightKeys("Double Click");
    });

    $(document).on("wheel", () => {
      this.highlightKeys("Scroll");
    });
    $(document).on("auxclick", () => {
      this.highlightKeys("Middle Click");
    });

    document.addEventListener("mouseup", (event) => {
      if (event.target.classList.contains("draggable")) {
        this.highlightKeys("Drop");
      }
    });
  }
  static getKeysPressed(event) {
    const keysPressed = [];
    if (event.ctrlKey) {
      keysPressed.push("Ctrl");
    }
    if (event.altKey) {
      keysPressed.push("Alt");
    }
    if (event.shiftKey) {
      keysPressed.push("Shift");
    }
    if (event.metaKey) {
      keysPressed.push("Cmd");
    }
    if (event.type === "auxclick") {
      keysPressed.push("Middle Click");
    }

    let mainKey = event.key;
    if (mainKey === " ") {
      mainKey = "Space";
    } else if (mainKey.toLowerCase() === "scroll") {
      mainKey = "Scroll";
    } else {
      mainKey = mainKey.toUpperCase();
    }
    return keysPressed;
  }
}

/**
 * @class LoadScreen
 * @description
 * acts as both a loading screen while
 * the topology renders initially and also
 * as a way to show errors when the rendering fails
 */

class LoadScreen {
  static LOAD_FAS = "fas fa-spinner loading";
  static ERROR_FAS = "fa-solid fa-circle-exclamation error";
  constructor() {
    this.$statusContent = $("#loader");
    this.$statusMsg = this.$statusContent.find("#statusMsg");
    this.loadInterval = null;
  }
  loading() {
    const msgs = ["Loading.", "Loading..", "Loading..."];
    this.clearLoadInterval();
    let index = 0;
    /* 
      if the loading interval still doesnt clear
      consider adding a class while it is loading 
      and, querying for it in interval &
      removing it when done 
    */
    this.loadInterval = setInterval(() => {
      index = (index + 1) % msgs.length;
      this.$statusMsg.fadeOut(100, function () {
        $(this).text(msgs[index]).fadeIn(200);
      });
    }, 500);
  }
  hide() {
    $("#loadScreen").fadeOut(500, () => {
      $("#canvas").removeClass("hidden");
      this.clearLoadInterval();
    });
  }
  /**
   *
   * @param {string} errorMsg
   * @returns {JQuery<HTMLElement>} - the retry button to add an event listener 2
   */
  toErrorMessage(errorMsg) {
    this.clearLoadInterval();
    this.$statusContent
      .find("i")
      .removeClass(LoadScreen.LOAD_FAS)
      .addClass(LoadScreen.ERROR_FAS);
    
    const genericError = "An error occurred rendering the topology, please try again.";
    const msg = errorMsg || genericError;

    this.$statusMsg.text(msg);
    const $retry = $("<div>", { id: 'retry-hold' });
    const $btn = $("<button>", { id: 'retryBtn' }).html(`
      <i class="fa-solid fa-arrow-rotate-right"></i>
        Retry ( ? )
    `);
    $retry.append($btn);
    this.$statusContent.append($retry);
    return $btn;
  }
  toLoading() {
    this.$statusContent
      .find("i")
      .removeClass(LoadScreen.ERROR_FAS)
      .addClass(LoadScreen.LOAD_FAS);

    this.$statusContent
      .find("#retry-hold")
      .remove();
      
    this.loading();
  }
  clearLoadInterval() {
    if(this.loadInterval) {
      clearInterval(this.loadInterval);
      this.loadInterval = null;
    }
  }
}
