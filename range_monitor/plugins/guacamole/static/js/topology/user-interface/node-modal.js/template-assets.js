
const assets = {
	checkbox: "modalCheckbox",
	filter: "filterTab",
	pager: "checkboxPager",
	container: "groupSelect",
  tab: "modalTab",
  field: "modalField",
  collapsible: "modalCollapse",
};

/**
 * manages & caches the template tags / document fragments
 * for commonly rendered assets, so they can be cloned
 */
const components = {
	assets: {},
	/**
	 * @param {string} templateId
	 * @returns {JQuery<HTMLElement>}
	 */
	cloneAsset(templateId) {
		if (!this.assets[templateId]) {
			this.registerAsset(templateId);
		}
		return this.assets[templateId].clone();
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
		this.assets[templateId] = $(cloned);
	}
};

export const assetFactory = {
  /**
	 * @param {ConnectionNode} connection
	 * @returns {JQuery<HTMLElement>}
	 */
	createCheckbox(connection) {
		const $checkbox = components.cloneAsset(assets.checkbox);
		$checkbox
			.attr("data-node-id", connection.identifier)
			.attr("data-active", connection.isActive())
			.find(".checkbox-label")
			.text(connection.name)
			.append(connection.getOsIcon());
		return $checkbox;
	},
	/**
	 * @param {Object} filterConfig - { text, count, icon, dataFilter }
	 * @returns {JQuery<HTMLElement>}
	 */
	createFilter(filterConfig) {
		const { text, count, icon, dataFilter } = filterConfig;
		const $filter = components.cloneAsset(assets.filter);
		$filter
			.attr("data-filter", dataFilter)
			.find(".filter-label")
			.prepend(`${text} (${count}) `)
			.find(".filter-icon")
			.addClass(icon);
		return $filter;
	},
  createField(title, value) {
    const $field = components.cloneAsset(assets.field);
    $field.find(".field-title").text(title);
    $field.find(".field-value").text(value);
    return $field;
  },
  createCollapse(title) {
    const $collapse = components.cloneAsset(assets.collapsible);
    const $content = $collapse.find(".collapsible-content");
    $collapse.find(".collapse-title").text(title);
    return { $container: $collapse, $content: $content };
  },
  createTab(title, fasIcon) {
    const $tab = components.cloneAsset(assets.tab);
    $tab.find(".tab-text").text(title);
    $tab.find(".tab-icon").addClass(fasIcon);
    return $tab;
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


