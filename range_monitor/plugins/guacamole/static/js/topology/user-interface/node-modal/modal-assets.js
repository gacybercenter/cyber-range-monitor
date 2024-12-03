import { assetFactory } from "./template-assets.js";
/** FieldOption [typedef]
 * @typedef {Object}
 * @property {string} fieldId
 * @property {string} titleId
 * @property {string} valueId
 * @property {string} fasIcon
 */
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
	static create(title, value) {
		return assetFactory.createField(title, value);
	}
}

export class Collapsible {
	/**
	 * @param {string} heading
	 */
	constructor(heading) {
		const { $container, $content } = assetFactory.createCollapse(heading);
		this.$container = $container;
		this.$content = $content;
	}
	/**
	 * @summary
	 * adds a either a list or single jQuery element to the collapsible.
	 * NOTE: if you use a list all elements must be a jQuery object or
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

export class ModalTab {
	/**
	 * @param {Object} windowConfig - { title: string, fasIcon: string }
	 */
	constructor(title, fasIcon) {
		this.$window = assetFactory.createTab(title, fasIcon);
		this.$content = $("<div>").addClass("tab-content").attr("role", "tabpanel");
		this.whenVisible = null;
	}
	/**
	 * @summary
	 * adds a either a list or single jQuery element to a tab.
	 * NOTE: if you use a list all elements must be a jQuery object or
	 * you will encounter unusual behavior.
	 * @param {JQuery<HTMLElement>} $content
	 */
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
}