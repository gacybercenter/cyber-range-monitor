import { assetFactory } from "./template-assets.js";
export {
	Field,
	Collapsible,
	ModalTab,
	SettingsToggler,
	OptionGroup,
	MODAL_ICONS,
	COLLAPSE_STYLE,
};

const assetUtils = {
	fadeIcons($icon, remove, add) {
		$icon.fadeOut(200, function () {
			$(this)
				.removeClass(remove)
				.addClass(add)
				.fadeIn(200);
		});
	},
};





// modalIcons
/**
 * @enum {Object}
 */
const MODAL_ICONS = Object.freeze({
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

// collapseStyle

/**
 * @enum {Object}
 */
const COLLAPSE_STYLE = Object.freeze({
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
	},
});

class Field {
	/**z
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
	 * @param {COLLAPSE_STYLE} COLLAPSE_STYLE - (optional)
	 */
	constructor(heading, iconStyle = COLLAPSE_STYLE.DEFAULT) {
		const { $container, $content } = assetFactory.createCollapse(
			heading,
			iconStyle
		);
		this.$container = $container;
		this.$content = $content;
	}

	/**
	 * @summary.
	 * NOTE: if you use a list of JQuery objs
	 * all elements must be a jQuery objects
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
	/**
	 * when the tab becomes the current tab,
	 * runs when the modal initially opens if the tab
	 * is the first tab index
	 * @param {callback} callback 
	 */
	setWhenVisible(callback) {
		this.whenVisible = callback;
	}
	/**
	 * when the tab has been rendered at least once 
	 * and becomes no longer visible; also runs if the
	 * modal closes 
	 * @param {callback} callback 
	 */
	setWhenHidden(callback) {
		this.whenHidden = callback;
	}
}

class OptionGroup {
	static OPTION_ON = "fas fa-check-square";
	static OPTION_OFF = "far fa-square";
	constructor(groupId, groupClass, optionClass) {
		this.$container = $("<div>")
			.addClass(`option-group ${groupClass}`)
			.attr("id", groupId);
		this.groupClass = groupClass;
		this.optionClass = optionClass;
		this.selectedOption = null;
	}
	/**
	 * @param {Object[]} optionData - [ { text: string, dataValue: string } ... ]
	 * @param {string} selectedOption - the default option or the previously selected option
	 */
	addOptions(optionData, selectedOption) {
		optionData.forEach((option) => {
			console.table(option);
			const $option = assetFactory.createSubOption(
				option,
				(option.dataValue === selectedOption),
				this.optionClass
			);
			this.$container.append($option);
		});
		console.log(this.$container);
		this.selectedOption = selectedOption;
	}
	/**
	 * toggles the appearance the options in the option group,
	 * and calls the callback passed with the data-value attribute 
	 * of the option selected.
	 * @param {callback} callback 
	 */
	onOptionClick(callback, predicate = null) {
		if(!this.selectedOption) {
			throw new Error("Cannot bind events to options that do not exist, please add options first");
		}
		const optSelector = `.${this.optionClass}`;
		const optionGroup = this; // to avoid "this" context issues inside event handler
		this.$container.on("click", optSelector, function () {
			const selectedOption = $(this).attr("data-value");
			let userFlag = predicate ? predicate(selectedOption) : false;
			if($(this).hasClass("selected") || userFlag) {
				optionGroup.errorAnimate();
				return;
			}
			const on = OptionGroup.OPTION_ON, off = OptionGroup.OPTION_OFF;
			const $options = optionGroup.$container.find(optSelector);
			$options.removeClass("selected");
			const $toggleOff = $options.not($(this)).find(".sub-option-icon");
			assetUtils.fadeIcons($toggleOff, on, off);
			
			$(this).addClass("selected");
			const $toggleOn = $(this).find(".sub-option-icon");
			assetUtils.fadeIcons($toggleOn, off, on);
			optionGroup.selectedOption = selectedOption;
			callback(selectedOption);
		});
	}
	errorAnimate() {
		this.$container.addClass("control-error");
		this.$container.one("animationend", () => {
			this.$container.removeClass("control-error");
		});
	}
	/**
	 * @param {string} value 
	 * @returns {JQuery<HTMLElement>}
	 */
	getSubOptionByValue(value) {
		return this.$container.find(`.sub-option[data-value="${value}"]`);	
	}
	get body() {
		return this.$container;
	}
}

class SettingsToggler {
	/**
	 * @param {string} togglerId 
	 * @param {Object} togglerIcons - { enabled: string, disabled: string }
	 * @param {string} text 
	 * @param {boolean} isEnabled 
	 */
	constructor(togglerId, togglerIcons, text, isEnabled) {
		this.$toggler = assetFactory.createSettingsToggler({
			togglerId,
			togglerIcons,
			text,
			isEnabled,
		});
		this.togglerIcons = togglerIcons;
	}
	/**
	 * when the toggler is clicked, toggles the appearance of the 
	 * toggler and passes the new state of the toggler to the callback
	 * @param {callback} callback 
	 */
	onTogglerClick(callback) {
		this.$toggler.on("click", () => {
			const shouldTurnOff = this.$toggler.hasClass("active");
			let remove = shouldTurnOff ? this.togglerIcons.enabled : this.togglerIcons.disabled;
			let add = shouldTurnOff ? this.togglerIcons.disabled : this.togglerIcons.enabled;
			assetUtils.fadeIcons(this.$toggler.find(".toggler-icon"), remove, add);
			this.$toggler.toggleClass("active");
			callback(!shouldTurnOff);
		});
	}
	get body() {
		return this.$toggler;
	}
}




