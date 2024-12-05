import { assetFactory } from "./template-assets.js";
export { Field, Collapsible, ModalTab, modalIcons, collapseStyle };

/**
 * @enum {Object}
 */
const modalIcons = Object.freeze({
	GENERAL_ICONS: {
		chartLine: "fa-solid fa-chart-line",
		summary: "fa-solid fa-list",
		gear: "fa-solid fa-gears",
		info: "fa-solid fa-circle-info",
		magnify: "fa-solid fa-magnifying-glass-chart",
		thumbtack: "fa-solid fa-thumbtack",
		warn: "fa-solid fa-exclamation",
		user: "fa-solid fa-user",
	},
	FIELD_ICONS: {
		id: "fa-regular fa-address-card",
		parentId: "fa-solid fa-passport",
		parent: "fa-solid fa-network-wired",
		active: "fa-solid fa-wifi",
		offline: "fa-solid fa-plug-circle-minus off-icon",
		online: "fa-solid fa-plug-circle-plus on-icon",
		userGroup: "fa-solid fa-users",
		wrench: "fa-solid fa-wrench",
		protocol: "fa-solid fa-satellite-dish",
		date: "fa-regular fa-calendar",
		pen: "fa-regular fa-pen-to-square",
		laptop: "fa-solid fa-laptop",
	},	
});

/**
 * @enum {Object}
 */
const collapseStyle = Object.freeze({
	DEFAULT: {
		collapsed: "fa-solid fa-caret-down",
		expanded: "fa-solid fa-caret-up",
	}, 
	FOLDER: {
		collapsed: "fa-solid fa-folder",
		expanded: "fa-solid fa-folder-open",
	},
	THUMBTACK: {
		collapsed: "fa-solid fa-thumbtack",
		expanded: "fa-solid fa-thumbtack-slash",
	}
});


class Field {
	/**
	 * @param {string} title
	 * @param {string} value
	 */
	constructor(title, value) {
		this.title = title;
		this.value = value;
	}
	/**
	 * @param {FieldOptions} fieldOptions
	 * @returns {JQuery<HTMLElement>} - the field element
	 */
	toHTML(fieldOptions = {}) {
		const { fieldId, titleId, valueId, fasIcon } = fieldOptions;
		const $field = assetFactory.createField(this.title, this.value);
		const cleanTitle = this.title.replace(/\s/g, "-");

		$field.attr("id", fieldId ?? `${cleanTitle}-field`);
		$field.find(".field-value").attr("id", valueId ?? `${cleanTitle}-value`);

		const $title = $field.find(".field-title");
		$title.attr("id", titleId ?? `${cleanTitle}-title`);
		if (fasIcon) {
			$title.prepend(`<i class="fas ${fasIcon}"></i> `); // <- leave an extra space for formatting
		}
		return $field;
	}
	/**
	 * @param {string} title
	 * @param {string} value
	 * @param {FieldOptions} fieldOptions
	 * @returns {JQuery<HTMLElement>}
	 */
	static create(title, value, fieldOptions = {}) {
		return new Field(title, value).toHTML(fieldOptions);
	}
}

class Collapsible {
	/**
	 * @param {string} heading
	 * @param {collapseStyle} collapseStyle - (optional)
	 */
	constructor(heading, iconStyle = collapseStyle.DEFAULT) {
		const { $container, $content } = assetFactory.createCollapse(
			heading,
			iconStyle
		);
		this.$container = $container;
		this.$content = $content;
	}
	/**
	 * @summary.
	 * NOTE: if you use a list of JQuery objs =>
	 * all elements must be a jQuery object or
	 * you will encounter unusual behavior.
	 * @param {JQuery<HTMLElement>} $htmlContent
	 */
	addContent($htmlContent) {
		this.$content.append($htmlContent);
	}

	/**
	 * @param {Field} field
	 * @param {FieldOptions} fieldOptions
	 */
	addField(field, fieldOptions = {}) {
		this.$content.append(field.toHTML(fieldOptions));
	}
	/**
	 * @returns {JQuery<HTMLElement>} - the collapsible element
	 */
	initalize() {
		return this.$container;
	}
	/**
	 *
	 * @param {string} fasIcon
	 */
	addHeaderIcon(fasIcon) {
		this.header.prepend(`<i class="fas ${fasIcon}"></i> `);
	}
	/**
	 * @param {string} heading
	 * @param {Field[]} fields
	 * @returns {JQuery<HTMLElement>} - the collapsible element
	 */
	get header() {
		return this.$container.find(".collapse-title");
	}
}

/**
 * @class ModalTab
 * @property {JQuery<HTMLElement>} $window - the tabs window
 * @property {JQuery<HTMLElement>} $content - the tabs content container
 * @property {Function|null} whenVisible - the callback when the tab is visible;
 * i.e when the tab is changed to
 * @property {Function|null} whenHidden - the callback when the tab is hidden;
 * i.e when the tab changes and the tab is then no longer visible
 */
class ModalTab {
	constructor(title, fasIcon) {
		this.$window = assetFactory.createTab(title, fasIcon);
		this.$content = $("<div>").addClass("tab-content").attr("role", "tabpanel");
		this.whenVisible = null;
		this.whenHidden = null;
	}
	addContent($content) {
		this.$content.append($content);
	}
	addTabId(tabId) {
		this.$window.attr("id", tabId);
		this.$content.attr("aria-labelledby", tabId).attr("id", `${tabId}Content`);
	}
	setWhenVisible(callback) {
		this.whenVisible = callback;
	}
	setWhenHidden(callback) {
		this.whenHidden = callback;
	}
}
