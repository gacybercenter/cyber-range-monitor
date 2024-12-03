/**
 * @enum {string}
 * contains the asset IDs to reduce errors and improve
 * consistency. if you ever expand this or add a new template
 * add an ID here and then to handle the values to display create
 * a method in assetFactory. :>
 */
const assetIds = {
	checkbox: "modalCheckbox",
	filter: "filterTab",
	pager: "checkboxPager",
	container: "groupSelect",
	tab: "modalTab",
	field: "modalField",
	collapsible: "modalCollapse",
	nodeBtn: "nodeButton",
};

/**
 * @summary
 * handles the logic for displaying the content
 * for all template tags.
 */
export const assetFactory = {
	/**
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
  /**
   * @param {string} btnText 
   * @param {string} btnClass 
   * @param {Object} btnIcons - { staticIcon: string, hoverIcon: string } 
   * @returns {JQuery<HTMLElement>}
   */
	createNodeBtn(btnText, btnClass, btnIcons) {
		const $btn = components.cloneAsset(assetIds.nodeBtn);
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
		const $tab = components.cloneAsset(assetIds.tab);
		$tab.find(".tab-text").text(title);
		$tab.find(".tab-icon").addClass(fasIcon);
		return $tab;
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
 * for commonly used assets allowing them to be cloned.
 * helps performance by reducing the number of times the DOM is
 * queried for the same elements and makes rendering the same HTML
 * over and over again less performance intensive.
 */
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
	 * @param {string[]} templateId
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