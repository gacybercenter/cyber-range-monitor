/* 
    When a node is double clicked
    we want a modal to appear to 
    display information about said 
    node.

    -Tabs for Modal 

    Connection Leaf Node 
    -General
    
    Name: [Node Name]
    Identifier: [Node Identifier]
    Parent Connection: [Parent_Name]
    Parent Identifier: [Parent_Identifier]

    Connection Status
    Active Connections: [activeConnections]
    Last Active: [lastActive] ?? 
    Protocol: [protocol]


    Connection Properties [collapse]
    if empty
        -No attributes have been set for
        this connection     
    forEach(node.attribute)
        -Attribute Name: [attributeName]
     
    Sharing Profile [collapse]
    if not sharing profile 
    No attributes have been set for
        this connection
    forEach(node.sharingProfile)
        -Attribute Name: [attributeName]

    Tab 2 - Node Controls 
    Connect to Node 
    Refresh Node Data 
    Kill Connection
    View Timeline  

    Tab 3 - Node Connection Group Topology 
    - Do not show if multiple nodes are selected 
    
    - Show the connection group topology in the modal 
*/

// modal.js
export { Modal, ModalHTML };

// modal types
/**
 * @typedef {Object} Field
 * @property {string} title - heading of the field
 * @property {string} value - value for field
 */

/**
 * @typedef {Object} TabContext
 * @property {string} tabId - ID of the tab
 * @property {string} title - bruh
 * @property {string} fasIcon - the font awesome icon class
 */

/**
 * @typedef {Object} TabData
 * @property {TabContext} tabContext - context of the tab
 * @property {JQuery<HTMLElement>[]} tabContent - the jQuery elements to add
 */

class ModalHTML {
  /**
   * creates HTML for a single field
   * @param {Field} fieldData
   * @returns {JQuery<HTMLElement>}
   */
  static createField(fieldData) {
    const { title, value } = fieldData;
    return $("<p>")
      .addClass("tab-field")
      .attr("id", `${title}-field`)
      .append(
        $("<strong>").addClass("field-title").text(`${title}:`),
        $("<span>").addClass("field-value").text(value)
      );
  }

  /**
   * creates a collapsible HTML element
   * @param {string} heading
   * @param {Field[]} fields
   * @returns {JQuery<HTMLElement>}
   */
  static createCollapsible(heading, fields) {
    const $collapsible = $("<div>").addClass("collapsible");
    const $header = $("<div>")
      .addClass("collapsible-header")
      .attr({
        tabindex: 0,
        "aria-expanded": "false",
        "aria-controls": `content-${heading
          .replace(/\s+/g, "-")
          .toLowerCase()}`,
      })
      .append(
        $("<span>").text(heading),
        $("<i>").addClass("fas fa-caret-down caret")
      );

    const $content = $("<div>")
      .addClass("collapsible-content")
      .attr("id", `content-${heading.replace(/\s+/g, "-").toLowerCase()}`);

    fields.forEach((field) => $content.append(ModalHTML.createField(field)));

    return $collapsible.append($header, $content);
  }

  /**
   * creates a tab element
   * from a tab context obj
   * @param {TabContext} tabObj
   * @returns {JQuery<HTMLElement>}
   */
  static createTab(tabObj) {
    const { tabId, title, fasIcon } = tabObj;
    return $("<div>")
      .addClass("tab")
      .attr({
        tabindex: 0,
        "data-tab": tabId,
        id: tabId,
        role: "tab",
        "aria-selected": "false",
        "aria-controls": `${tabId}Content`,
      })
      .append($("<i>").addClass(fasIcon), $("<span>").text(title));
  }

  /**
   * creates a tab content element
   * @param {TabContext} tabContext
   * @param {JQuery<HTMLElement>[]} tabElements
   * @returns {JQuery<HTMLElement>}
   */
  static createTabContent(tabContext, tabElements) {
    return $("<div>")
      .addClass("tab-content")
      .attr({
        id: `${tabContext.tabId}Content`,
        role: "tabpanel",
        "aria-labelledby": tabContext.tabId,
      })
      .append(tabElements);
  }
}

class Modal {
  constructor() {
    this.$overlay = $(".modal-overlay");
    this.$modal = this.$overlay.find(".modal");
    this.$modalHeader = this.$modal.find(".modal-header h2");
    this.$closeBtn = this.$modal.find(".close-btn");
    this.$windowTabs = this.$modal.find(".tabs");
    this.$modalContent = this.$modal.find(".tab-content-container");
    this.renderedTabs = [];
    this.activeTabIndex = -1;
    this.isAnimating = false;
    this.isOpen = false;

    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.bindEvents();
  }

  /**
   * ensures the modal is closed before
   * events are triggered
   * @param {Function} callback - the event handler to guard
   * @returns {Function} - the guarded event handler
   */
  guardEvent(callback) {
    return (...args) => {
      if (!this.isOpen) return;
      return callback(...args);
    };
  }

  init(title, modalTabData) {
    if (this.isOpen) {
      return;
    }
    this.clearModal();
    this.$modalHeader.text(title);
    modalTabData.forEach((tabData) => this.addTab(tabData));

    if (modalTabData.length === 0) {
      throw new Error("Modal must have at least one tab");
    }
    this.switchTab(0, false);
  }

  clearModal() {
    this.$windowTabs.empty();
    this.$modalContent.empty();
    this.renderedTabs = [];
    this.activeTabIndex = -1;
  }

  openModal() {
    if (this.isOpen) {
      return;
    }
    this.activeTabIndex = 0;
    this.$overlay.fadeIn(200, () => {
      this.$windowTabs
        .find(".tab")
        .eq(0)
        .addClass("active")
        .attr("aria-selected", "true")
        .focus();
      this.$modalContent.find(".tab-content").eq(0).addClass("active").show();
      $(document).on("keydown", this.handleKeyDown);
    });
    this.isOpen = true;
  }

  closeModal() {
    if (!this.isOpen) {
      return;
    }
    this.$overlay.fadeOut(200, () => {
      $(document).off("keydown", this.handleKeyDown);
    });
    this.isOpen = false;
  }

  addTab(tabData) {
    const { tabContext, tabContent } = tabData;
    const $tabWindow = ModalHTML.createTab(tabContext);
    const $tabContent = ModalHTML.createTabContent(tabContext, tabContent);

    this.$windowTabs.append($tabWindow);
    this.$modalContent.append($tabContent);
    this.renderedTabs.push($tabContent);
  }

  /**
   * switches to the next or previous tab
   * @param {boolean} [previous=false] - if true, switches to previous tab
   */
  switchToAdjacentTab(previous = false) {
    if (!this.isOpen) {
      return;
    }

    const tabCount = this.renderedTabs.length;
    if (tabCount <= 1) {
      return;
    }

    let newIndex;
    if (previous) {
      newIndex =
        this.activeTabIndex <= 0 ? tabCount - 1 : this.activeTabIndex - 1;
    } else {
      newIndex =
        this.activeTabIndex >= tabCount - 1 ? 0 : this.activeTabIndex + 1;
    }

    this.switchTab(newIndex);
    this.$windowTabs.find(".tab").eq(newIndex).focus();
  }

  switchTab(index, animate = true) {
    if (!this.isOpen || this.isAnimating || index === this.activeTabIndex) {
      return;
    }

    this.isAnimating = true;
    const $tabs = this.$windowTabs.find(".tab");
    const $tabContents = this.$modalContent.find(".tab-content");
    const $prevContent = $tabContents.eq(this.activeTabIndex);
    const $newContent = $tabContents.eq(index);

    $tabs
      .removeClass("active")
      .attr("aria-selected", "false")
      .eq(index)
      .addClass("active")
      .attr("aria-selected", "true");

    const switchContent = () => {
      $tabContents.removeClass("active").hide();
      $newContent.addClass("active").show();
      this.activeTabIndex = index;
      this.isAnimating = false;
    };

    if (this.activeTabIndex === -1 || !animate) {
      switchContent();
      return;
    }

    $prevContent.fadeOut(200, () => {
      $newContent.fadeIn(200, () => {
        this.isAnimating = false;
        this.activeTabIndex = index;
      });
    });
  }

  handleKeyDown(event) {
    if (!this.isOpen) return;
    
    switch (event.key) {
      case "Escape":
        this.closeModal();
        break;
      case "Tab":
        event.preventDefault();
        const flag = !event.shiftKey ? false : true;
        this.switchToAdjacentTab(flag);
        break;
      case "ArrowRight":
        event.preventDefault();
        this.switchToAdjacentTab(false);
        break;
      case "ArrowLeft":
        event.preventDefault();
        this.switchToAdjacentTab(true);
        break;
    }
  }

  bindEvents() {
    this.$closeBtn.on(
      "click",
      this.guardEvent(() => this.closeModal())
    );

    this.$overlay.on(
      "click",
      this.guardEvent((event) => {
        if ($(event.target).is(this.$overlay)) {
          this.closeModal();
        }
      })
    );

    this.$windowTabs
      .on(
        "click",
        ".tab",
        this.guardEvent((event) => {
          const index = $(event.currentTarget).index();
          this.switchTab(index);
        })
      )
      .on(
        "keypress",
        ".tab",
        this.guardEvent((event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            const index = $(event.currentTarget).index();
            this.switchTab(index);
          }
        })
      );

    this.$modalContent.on(
      "click keypress",
      ".collapsible-header",
      this.guardEvent((event) => {
        if (
          event.type === "keypress" &&
          event.key !== "Enter" &&
          event.key !== " "
        ) {
          return;
        }

        event.preventDefault();
        const $header = $(event.currentTarget);
        const $content = $header.next(".collapsible-content");
        const $caret = $header.find(".caret");
        const isExpanded = $content.hasClass("expanded");

        $header.attr("aria-expanded", !isExpanded);
        $content.toggleClass("expanded");
        $caret.toggleClass("rotated");
      })
    );
  }
}