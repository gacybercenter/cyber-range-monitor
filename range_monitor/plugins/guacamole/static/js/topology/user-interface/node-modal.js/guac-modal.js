// topology/user-interface/node-modal/guac-modal.js
import { assetFactory } from "./template-assets.js";

export class Modal {
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
    this.onClose = null;
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
      if (!this.isOpen) {
        return;
      }
      return callback(...args);
    };
  }

  /**
   * @param {string} title - modal title 
   * @param {ModalTab[]} modalTabs - must be an array
   * @returns {void}
   */
  init(title, modalTabs) {
    if (this.isOpen) {
      return;
    }
    if (modalTabs.length === 0) {
      throw new Error("Modal must have at least one tab");
    }
    this.clearModal();
    this.$modalHeader.text(title);
    modalTabs.forEach((modalTab) => this.addTab(modalTab));
    this.switchTab(0, false);
  }
  /**
   * resets the modal & it's HTML content
   */
  clearModal() {
    this.$windowTabs.empty();
    this.$modalContent.empty();
    this.renderedTabs = [];
    this.activeTabIndex = -1;
  }
  /**
   * @param {Function} onClose - callback for when the modal closes  
   * @returns {void}
   */
  openModal(onClose = null) {
    if (this.isOpen) {
      return;
    }
    if(onClose) {
      this.onClose = onClose;
    }
    this.activeTabIndex = 0;
    this.$overlay.fadeIn(200, () => {
      this.$windowTabs
        .find(".tab")
        .eq(0)
        .addClass("active")
        .attr("aria-selected", "true")
        .focus();
      this.$modalContent
        .find(".tab-content")
        .eq(0)
        .addClass("active")
        .show();
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
    if(this.onClose) {
      this.onClose();
    }
  }
  /**
   * @param {ModalTab} tabData 
   */
  addTab(modalTab) {
    const { $window, $content } = modalTab;
    this.$windowTabs.append($window);
    this.$modalContent.append($content);
    this.renderedTabs.push($content);
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
    this.$windowTabs
      .find(".tab")
      .eq(newIndex)
      .focus();
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
    if (!this.isOpen) {
      return;
    }
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

export class Field {
  /**
   * @param {string} title 
   * @param {string} value 
   */
  constructor(title, value) {
    this.title = title;
    this.value = value;
  }
  /**
   * @returns {JQuery<HTMLElement>}
   */
  toHTML(fieldId = null, titleId = null, valueId = null) {
    const tryAddId = ($tag, id) => {
      if(id) {
        $tag.attr("id", id);
      }
    };
    const $field = assetFactory.createField(this.title, this.value);
    tryAddId($field, fieldId);
    tryAddId($field.find(".field-title"), titleId);
    tryAddId($field.find(".field-value"), valueId);
    return $field;
  }
  static create(title, value) {
    return assetFactory.createField(title, value);
  }
}

export class Collapsible {
  /**
   * @param {string} heading 
   */
  constructor(heading) {
    const { $container, $content} = assetFactory.createCollapse(heading);
    this.$container = $container;
    this.$content = $content;
  }
  /**
   * @param {JQuery<HTMLElement>} $htmlContent 
   */
  addContent($htmlContent) {
    this.$content.append($htmlContent);
  }

  /**
   * @param {Field} field 
   */
  addField(field) {
    this.$content.append(field.toHTML());
  }
  /**
   * @returns {JQuery<HTMLElement>} - the collapsible element
   */
  initalize() {
    return this.$container;
  }
  /**
   * @param {string} heading 
   * @param {Field[]} fields 
   * @returns {JQuery<HTMLElement>} - the collapsible element
   */
  static createGeneric(heading, fields) {
    const collapsible = new Collapsible(heading);
    fields.forEach(field => {
      collapsible.addField(field)
    });
    return collapsible.initalize();
  }
  get header() {
    return this.$container.find(".collapse-title");
  }
}

export class ModalTab {
  /**
   * @param {Object} windowConfig - { title: string, fasIcon: string } 
   */
  constructor(title, fasIcon) {
    this.$window = assetFactory.createTab(title, fasIcon);
    this.$content = $("<div>").addClass("tab-content").attr("role", "tabpanel");
  }
  addContent($content) {
    this.$content.append($content);
  }
  addTabId(tabId) {
    this.$window.attr("id", tabId);
    this.$content.attr("aria-labelledby", tabId)
      .attr("id", `${tabId}Content`); 
  }
}





