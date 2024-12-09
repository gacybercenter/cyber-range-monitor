export { assetFactory, ASSET_IDS };


/**
 * @typedef TogglerPreference
 * @property {string} togglerId
 * @property {Object} togglerIcons - { enabled: string, disabled: string }
 * @property {string} text
 * @property {boolean} isEnabled
 */





/**
 * @enum {string}
 * contains the asset IDs to reduce errors and improve
 * consistency. if you ever expand this or add a new template
 * add an ID here
 */
const ASSET_IDS = Object.freeze({
	checkbox: "modalCheckbox",
	filter: "filterTab",
	pager: "pageHandler",
	container: "groupSelect",
	tab: "modalTab",
	field: "modalField",
	collapsible: "modalCollapse",
	nodeBtn: "nodeButton",
	groupSelect: "groupSelect",
	settingsToggler: "settingsToggler",
	subOption: "subOption",
});

const components = {
	assetCache: {},
	/**
	 * @param {string} templateId
	 * @returns {JQuery<HTMLElement>}
	 */
	cloneAsset(templateId) {
		if (!this.assetCache[templateId]) {
			this.registerAsset(templateId);
		}
		return this.assetCache[templateId].clone();
	},
	/**
	 * @param {string} templateId
	 */
	registerAsset(templateId) {
		const template = document.getElementById(templateId);
		if (!template) {
			throw new Error(
				`[COMPONENT_ERROR] Template with id ${templateId} not found`
			);
		}
		const cloned = template.content.cloneNode(true).children[0];
		this.assetCache[templateId] = $(cloned);
	},
};

const assetFactory = {
	/**
	 * @param {string} title
	 * @param {string} value
	 * @returns {JQuery<HTMLElement>}
	 */
	createField(title, value) {
		const $field = components.cloneAsset(ASSET_IDS.field);
		$field.find(".field-title").text(title);
		$field.find(".field-value").text(value);
		return $field;
	},
	createGroupSelect() {
		return components.cloneAsset(ASSET_IDS.groupSelect);
	},
	/**
	 * @param {string} btnText
	 * @param {string} btnClass
	 * @param {Object} btnIcons - { staticIcon: string, hoverIcon: string }
	 * @returns {JQuery<HTMLElement>}
	 */
	createNodeBtn(btnText, btnClass, btnIcons) {
		const $btn = components.cloneAsset(ASSET_IDS.nodeBtn);
		$btn.addClass(btnClass);

		const replaceIcon = ($tag, old, update) => {
			$tag.fadeOut(100, function () {
				$(this).removeClass(old).addClass(update).fadeIn(100);
			});
		};

		$btn.find(".node-btn-text").text(btnText);
		const $btnIcon = $btn.find(".node-btn-icon");
		const { staticIcon, hoverIcon } = btnIcons;
		$btnIcon.addClass(staticIcon);
		$btn.hover(
			() => replaceIcon($btnIcon, staticIcon, hoverIcon),
			() => replaceIcon($btnIcon, hoverIcon, staticIcon)
		);
		return $btn;
	},
	/**
	 * note: events are added by Modal class
	 * @param {string} title
	 * @param {Object} collapseType
	 * @returns {Object{ $container: JQuery<HTMLElement>, $content: JQuery<HTMLElement> }}
	 */
	createCollapse(title, collapseType) {
		const $collapse = components.cloneAsset(ASSET_IDS.collapsible);
		const $content = $collapse.find(".collapsible-content");
		$collapse.find(".collapse-title").text(title);
		$collapse
			.find(".collapse-toggle")
			.attr("data-expanded-icon", collapseType.expanded)
			.attr("data-collapsed-icon", collapseType.collapsed)
			.addClass(collapseType.collapsed);
		return {
			$container: $collapse,
			$content: $content,
		};
	},
	/**
	 * creates a tab window in the modal
	 * @param {string} title - title of the tab
	 * @param {string} fasIcon - fas icon class
	 * @returns {JQuery<HTMLElement>}
	 */
	createTab(title, fasIcon) {
		const $tab = components.cloneAsset(ASSET_IDS.tab);
		$tab.find(".tab-text").text(title);
		$tab.find(".tab-icon").addClass(fasIcon);
		return $tab;
	},
	/**
	 * @param {ConnectionNode} connection
	 * @returns {JQuery<HTMLElement>}
	 */
	createCheckbox(connection) {
		const $checkbox = components.cloneAsset(ASSET_IDS.checkbox);
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
		const $filter = components.cloneAsset(ASSET_IDS.filter);
		$filter
			.attr("data-filter", dataFilter)
			.find(".filter-label")
			.prepend(`${text} (${count}) `)
			.find(".filter-icon")
			.addClass(icon);
		return $filter;
	},
	createPager() {
		return components.cloneAsset(ASSET_IDS.pager);
	},
	/**
	 * @param {TogglerPreference} togglerPreferences 
	 * @returns {JQuery<HTMLElement>}
	 */
	createSettingsToggler(togglerPreferences) {
		const { togglerId, togglerIcons, text, isEnabled } = togglerPreferences;
		const $toggler = components.cloneAsset(ASSET_IDS.settingsToggler); 
		$toggler
			.attr("id", togglerId)
			.addClass(isEnabled? "active" : "");

		$toggler.find(".toggler-icon")
			.addClass(isEnabled? togglerIcons.enabled : togglerIcons.disabled);

		$toggler.find(".toggler-text").text(text);
		return $toggler;		
	},
	/**
	 * 
	 * @param {OptionGroupConfig} subOptionConfig 
	 */
	createSubOption({ title, dataValue }, isEnabled, optionClass) {
		const $subOption = components.cloneAsset(ASSET_IDS.subOption);
		$subOption
			.attr("data-value", dataValue)
			.addClass(isEnabled? "active" : "")
			.find(".sub-option-text")
			.text(title);
		$subOption
			.find(".sub-option-icon")
			.addClass(isEnabled ? "fas fa-check-square" : "far fa-square");
	},
};
