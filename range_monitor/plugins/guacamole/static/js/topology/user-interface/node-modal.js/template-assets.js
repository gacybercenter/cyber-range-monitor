

/**
 * @enum {string}
 * contains the asset IDs to reduce
 * errors and improve consitency 
 */
const assetIds = {
	checkbox: "modalCheckbox",
	filter: "filterTab",
	pager: "checkboxPager",
	container: "groupSelect",
  tab: "modalTab",
  field: "modalField",
  collapsible: "modalCollapse",
  nodeBtn: "nodeBtn",
};

export const assetFactory = {
  /**
   * @summary
   * creates a field with a title and value
   * @param {string} title 
   * @param {string} value 
   * @returns {JQuery<HTMLElement>} 
   */
  createField(title, value) {
    const $field = components.cloneAsset(assetIds.field);
    $field.find(".field-title").text(title);
    $field.find(".field-value").text(value);
    return $field;
  },
  createNodeBtn(btnText, btnClass, btnIcons) {
    const $btn = components.cloneAsset(assetIds.nodeBtn);
    $btn.addClass(btnClass);
    $btn.find(".node-btn-text").text(btnText);
    const $btnIcon = $btn.find(".node-btn-icon");
    const { staticIcon, hoverIcon } = btnIcons;
    $btnIcon
      .addClass(staticIcon)
      .hover(
        function() {
          $(this).removeClass(staticIcon).addClass(hoverIcon);
        }, 
        function() {
          $(this).removeClass(hoverIcon).addClass(staticIcon);
        }
      );
    return $btn;
  },
  /**
   * @summary
   * creates a collapsible section of content,
   * events are added by Modal class 
   * @param {string} title 
   * @returns {Object{ $container: JQuery<HTMLElement>, $content: JQuery<HTMLElement> }}
   */
  createCollapse(title) {
    const $collapse = components.cloneAsset(assetIds.collapsible);
    const $content = $collapse.find(".collapsible-content");
    $collapse.find(".collapse-title").text(title);
    return { 
      $container: $collapse, 
      $content: $content 
    };
  },
  /**
   * creates the tab window in the modal
   * @param {string} title - title of the tab
   * @param {string} fasIcon - fas icon class 
   * @returns {JQuery<HTMLElement>}
   */
  createTab(title, fasIcon) {
    const $tab = components.cloneAsset(assetIds.tab);
    $tab.find(".tab-text").text(title);
    $tab.find(".tab-icon").addClass(fasIcon);
    return $tab;
  },
  /**
   * creates the container for tab content
   * @param {string} tabId 
   * @param {JQuery<HTMLElement>} $contents 
   * @returns {JQuery<HTMLElement>}
   */
  createTabContent($contents) {
    return $("<div>")
      .addClass("tab-content")
      .attr("role", "tabpanel")
      .append($contents);
  },
  /**
   * @summary
   * creates a checkbox in the group selector
   * for connection groups
	 * @param {ConnectionNode} connection
	 * @returns {JQuery<HTMLElement>}
	 */
	createCheckbox(connection) {
		const $checkbox = components.cloneAsset(assetIds.checkbox);
		$checkbox
			.attr("data-node-id", connection.identifier)
			.attr("data-active", connection.isActive())
			.find(".checkbox-label")
			.text(connection.name)
			.append(connection.getOsIcon());
		return $checkbox;
	},
	/**
   * @summary
   * creates a "filter" tab / button in the
   * group selector 
	 * @param {Object} filterConfig - { text, count, icon, dataFilter }
	 * @returns {JQuery<HTMLElement>}
	 */
	createFilter(filterConfig) {
		const { text, count, icon, dataFilter } = filterConfig;
		const $filter = components.cloneAsset(assetIds.filter);
		$filter
			.attr("data-filter", dataFilter)
			.find(".filter-label")
			.prepend(`${text} (${count}) `)
			.find(".filter-icon")
			.addClass(icon);
		return $filter;
	},
};




/**
 * @summary
 * manages & caches the template tags / document fragments
 * for commonly rendered assets, so they can be cloned. 
 * this approach reduces the number of times the DOM is
 * queried for the same elements and makes rendering the same HTML
 * over and over again less performance intensive.
 */
const components = {
	assetIds: {},
	/**
	 * @param {string} templateId
	 * @returns {JQuery<HTMLElement>}
	 */
	cloneAsset(templateId) {
		if (!this.assetIds[templateId]) {
			this.registerAsset(templateId);
		}
		return this.assetIds[templateId].clone();
	},
	/**
	 * @param {string[]} templateId
	 */
	registerAsset(templateId) {
		const template = document.getElementById(templateId);
		if (!template) {
			throw new Error(`[COMPONENT_ERROR] Template with id ${templateId} not found`);
		}
		const cloned = template.content.cloneNode(true).children[0];
		this.assetIds[templateId] = $(cloned);
	}
};














// const selectors = {
//   unchecked: "fa-regular fa-rectangle-xmark icon icon-deselected",
//   checked: "fa-square-check icon-selected",
// }


/* 
<div class="checkbox-item checkbox-option" 
  data-node-id="${connection.identifier}" 
  data-active="${connection.isActive()}"
>
  <i class="fa-regular fa-rectangle-xmark icon icon-deselected"></i>
  <label class="checkbox-label">
    ${connection.name} ${connection.getOsIcon()}
  </label>
</div>
*/




/**
 * toggler options
 * {
    text: "Enable Paragraph",
    icons: {
      onIcon: "fa-solid fa-play",
      offIcon: "fa-solid fa-pause",
    },
    activeClass: "active",
    inactiveClass: "inactive",
  }
 */
export class Toggler {
  constructor(options, flag) {
    this.$tag = templateManager.toggler.clone();
    this.$icon = this.$tag.find(".toggler-icon");
    this.$text = this.$tag.find(".toggler-text");
    this.options = options;
    this.changeText(options.text);
    this.toggle(flag);
  }
  toggle(flag) {
    if (flag) {
      this.enable();
    } else {
      this.disable();
    }
  }
  enable() {
    this.$tag
      .removeClass(this.options.inactiveClass)
      .addClass(this.options.activeClass);
    this.$icon
      .removeClass(this.options.icons.offIcon)
      .addClass(this.options.icons.onIcon);
  }
  disable() {
    this.$tag
      .removeClass(this.options.activeClass)
      .addClass(this.options.inactiveClass);
    this.$icon
      .removeClass(this.options.icons.onIcon)
      .addClass(this.options.icons.offIcon);
  }
  get button() {
    return this.$tag;
  }
  changeText(text) {
    this.$text.text(text);
  }
}
/* 
  checkbox options 
  {
    text: [str],
    valueText: [str],
    dataField: [str], (e.g "speed" would be "data-speed")
    dataValue: [str]
  }
*/
export class Checkbox {
  constructor(options) {
    this.$tag = templateManager.subOption.clone();
    this.$icon = this.$tag.find(".sub-icon");
    this.$text = this.$tag.find(".option-text");
    this.$val = this.$tag.find(".option-val");
    this.id = options.id;
    this.options = options;
    this.init();
  }
  init() {
    const { dataField, dataValue } = this.options;
    this.$tag
      .data(dataField, dataValue)
      .attr("id", this.id);
    this.$text.text(this.options.text);
    this.$val.text(this.options.valueText);
    this.uncheck();
    /*
      
    */
  }
  toggle(flag = null) {
    if (!flag) {
      flag = this.$tag.hasClass("selected");
    }
    if (this.$tag.hasClass("selected")) {
      this.uncheck();
    } else {
      this.check();
    }
  }
  check() {
    this.$tag.addClass("selected");
    this.$icon
      .removeClass("far fa-square")
      .addClass("fas fa-check-square");
  }
  uncheck() {
    this.$tag.removeClass("selected");
    this.$icon
      .removeClass("fas fa-check-square")
      .addClass("far fa-square");
  }
  isChecked() {
    return this.$tag.hasClass("selected");
  }
}


