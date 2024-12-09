
import { assetFactory } from "./template-assets.js";

/**
 * renders the group selector & adds the necessary event handlers
 * @param {string[]} selectedIds
 * @param {ConnectionNode[]} pageData
 * @returns {Object} - groupSelector
 */
export function renderGroupSelector(pageData) {
	const groupSelector = new GroupSelector();
	const filterConfigs = getFilterConfigs(pageData);
	
	groupSelector.init(pageData, filterConfigs);
	groupSelector.renderPage();
	
	groupSelector.addEvent("click", ".filter-button", function () {
		eventHandlers.filterClick($(this), groupSelector);
	});

	groupSelector.addEvent("click", ".checkbox", function () {
		eventHandlers.checkboxClick($(this), groupSelector);
		eventHandlers.updateCounter(groupSelector);
	});

	groupSelector.addEvent("click", ".select-all", () => {
		eventHandlers.selectAllClick(groupSelector);
	});

	groupSelector.addEvent("click", ".pager-icon", function () {
		eventHandlers.onPageClick($(this), groupSelector);
	});
	return groupSelector;
}

/**
 * @enum {string}
 * @description contains all the icons used in the Group Selector
 * bc if I forget that fas class names, so will you =)
 */
const assetIcons = Object.freeze({
	checkbox: {
		on: "fa-circle-check",
		off: "fa-circle-xmark",
	},
	selectAll: {
		on: "fa-hand-pointer",
		off: "fa-arrow-pointer",
	},
	pagination: {
		left: "fa-arrow-left",
		right: "fa-arrow-right",
	},
	filterIcons: {
		all: "fa-solid fa-users-rays",
		inactive: "fa-solid fa-power-off",
		active: "fa-solid fa-signal",
	},
	on: "active",
});

/** FilterConfig
 * @typedef FilterConfig
 * @property {string} text - the text of the filter button
 * @property {number} count - number of items that match the filter criteria
 * @property {string} icon - the filter button fas icon
 * @property {string} dataFilter - the data-filter attribute value; used to determine which filter is which
 */

/**
 * sets the props configurations for the 
 * 3 filter buttons => All, Active, Inactive
 * @param {ConnectionNode[]} pageData 
 * @returns {FilterConfig[]} 
 */
const getFilterConfigs = (pageData) => {
	const { filterIcons } = assetIcons;
	const activeConnections = pageData.filter((n) => n.isActive()) || [];
	const showAllFilter = {
		text: "All",
		count: pageData.length,
		icon: filterIcons.all,
		dataFilter: "all",
	};
	const inactiveFilter = {
		text: "Inactive",
		count: pageData.length - activeConnections.length,
		icon: filterIcons.inactive,
		dataFilter: "inactive",
	};
	const activeFilter = {
		text: "Active",
		count: activeConnections.length,
		icon: filterIcons.active,
		dataFilter: "active",
	};
	return [showAllFilter, inactiveFilter, activeFilter];
};

/**
 * @class GroupSelector
 * @description manages the state & renders the
 * HTML for the Group Selection for Connection groups
 * @property {ConnectionNode[]} filteredItems - the "filtered" items,
 * (e.g the active filter would make it store all active connections)
 * @property {ConnectionNode[]} pageData - all Child ConnectionNodes of the Group, does not change.
 * @property {Pager} pager - the pager object for the Group Selector, handles logic for paging.
 */
class GroupSelector {
	static ITEMS_PER_PAGE = 12; // change as needed
	constructor() {
		this.filteredItems = [];
		this.pageData = [];
		this.selectedIds = [];
		this.pager = null;
		this.$content = null;
	}

	/**
	 * @param {ConnectionNode[]} connections
	 * @param {FilterConfig[]} filterConfigs
	 * @returns {JQuery<HTMLElement>}
	 */
	init(connections, filterConfigs) {
		this.pageData = connections;
		this.filteredItems = connections;
		this.pager = new Pager(GroupSelector.ITEMS_PER_PAGE);
		this.pager.init(connections);
		this.$content = assetFactory.createGroupSelect();
		this.renderFilters(filterConfigs);
		const page = assetFactory.createPager();
		this.$content
			.find(".pagination-container")
			.append(page);
	}
	/**
	 * @param {string} eventType - type of event (e.g click)
	 * @param {string} eventTarget  - the selector of the target element
	 * @param {callback} callback 
	 */
	addEvent(eventType, eventTarget, callback) {
		this.$content.on(eventType, eventTarget, callback);
	}
	/**
	 * maps all of the current filtered items to their ids
	 * i.e the ones that can be visible on any of the pages
	 * of the selected filter
	 * @returns {string[]}
	 */
	get visibleIds() {
		return this.filteredItems.map(n => n.identifier);
	}
	/**
	 * @returns {string[]}
	 */
	get checkedIds() {
		return this.selectedIds;
	}
	/**
	 * @returns {JQuery<HTMLElement>[]}
	 */
	get checkboxes() {
		return this.findTag(".checkbox");
	}
	/**
	 * @param {FilterConfig[]} filterConfigs - { text: string, count: number, icon: string, dataFilter: string }
	 */
	renderFilters(filterConfigs) {
		const $filters = this.findTag(".filters");
		filterConfigs.forEach(filterConfig => {
			const $filter = assetFactory.createFilter(filterConfig);
			if (filterConfig.text === "All") {
				$filter.addClass(assetIcons.on);
			}
			$filters.append($filter);
		});
	}

	/**
	 * @param {string} selector
	 * @returns {JQuery<HTMLElement>}
	 */
	findTag(selector) {
		const $tag = this.$content.find(selector);
		if ($tag.length === 0) {
			console.warn(`GroupSelector: could not find a tag with a "${selector}" selector`);
		}
		return $tag;
	}
	/**
	 * renders a single page and empties the checkbox container
	 * and then recreates it; this approach avoids mutating the existing
	 * references bc believe me that gets messy / buggy.
	 */
	renderPage() {
		const pageContents = this.pager.getPageContent(this.filteredItems);
		const $checkboxHolder = this.findTag(".checkbox-container");
		$checkboxHolder.empty();
		pageContents.forEach(connection => {
			const { identifier } = connection;
			const $checkbox = assetFactory.createCheckbox(connection);
			if (this.selectedIds.includes(identifier)) {
				iconTogglers.enableCheck($checkbox);
				$checkbox.addClass("active");
			}
			$checkboxHolder.append($checkbox);
		});

		const $pageIcons = this.findTag(".pager-icon");
		const needPages = (this.pager.totalPages > 1);
		$pageIcons.prop("disabled", !needPages);
		this.updatePageInfo();
		eventHandlers.updateCounter(this);
	}
	updatePageInfo() {
		const { index, totalPages } = this.pager;
		this.findTag(".pager-label")
			.text(`Page ( ${index + 1} / ${totalPages} ) `);
	}
	/**
	 * @param {string} action
	 * @param {string[]} selectedIds
	 */
	changePage(action) {
		// note, pager handles indexing in setter
		if (action === "left") {
			this.pager.index--;
		} else if (action === "right") {
			this.pager.index++;
		}
		this.renderPage();
	}

	/**
	 * @param {string} newFilter
	 */
	changeFilter(newFilter) {
		switch (newFilter) {
			case "active":
				this.filteredItems = this.pageData.filter(n => n.isActive());
				break;
			case "inactive":
				this.filteredItems = this.pageData.filter(n => !n.isActive());
				break;
			case "all":
				this.filteredItems.length = 0;
				this.filteredItems.push(...this.pageData);
				break;
			default:
				throw new Error(`Unknown Group Select Filter "${newFilter}"`);
		}
		this.pager.init(this.filteredItems);
		this.updatePageInfo();
		this.renderPage();
	}
	uncheckAll() {
		this.checkboxes.each(function () {
			iconTogglers.disableCheck($(this));
		});
	}
	checkAll() {
		// anon func to preserve context of "this"
		const contains = (id) => {
			return this.selectedIds.includes(id);
		};
		this.checkboxes.each(function () {
			const nodeId = $(this).attr("data-node-id");
			if (!contains(nodeId)) {
				iconTogglers.enableCheck($(this));
			}
		});
	}
	/**
	 * @param {string[]} filteredNodes
	 */
	resetSelection(filteredNodes) {
		for (let i = this.selectedIds.length - 1; i >= 0; i--) {
			if (filteredNodes.includes(this.selectedIds[i])) {
				this.selectedIds.splice(i, 1);
			}
		}
	}

	/**
	 * @param {string[]} filteredNodes
	 */
	buildSelection(filteredNodes) {
		filteredNodes.forEach((id) => {
			if (!this.selectedIds.includes(id)) {
				this.selectedIds.push(id);
			}
		});
	}
}

const eventHandlers = {
	/**
	 * @param {GroupSelector} groupSelector
	 */
	updateCounter(groupSelector) {
		const { selectedIds, filteredItems } = groupSelector;

		const $selectAll = groupSelector.findTag(".select-all");
		
		const allChecked = (selectedIds.length === filteredItems.length);
		const selectAllOn = $selectAll.hasClass("active");

		if (allChecked && !selectAllOn) {
			iconTogglers.selectAllOn($selectAll);
		} else if (!allChecked && selectAllOn) {
			iconTogglers.selectAllOff($selectAll);
		}
		
		const $counter = groupSelector.findTag("#selectedCounter");
		const counterAtMax = $counter.hasClass("reached");
		if (allChecked && !counterAtMax) {
			$counter.addClass("reached");
		} else if (!allChecked && counterAtMax) {
			$counter.removeClass("reached");
		}
		$counter.text(`( ${selectedIds.length} / ${filteredItems.length} )`);
	},
	/**
	 * @param {JQuery<HTMLElement>} $filterBtn
	 * @param {groupSelector} groupSelector
	 */
	filterClick($filterBtn, groupSelector) {
		const newFilter = $filterBtn.attr("data-filter");
		groupSelector.changeFilter(newFilter);

		$filterBtn
			.addClass("active")
			.siblings()
			.removeClass(assetIcons.on);

		groupSelector.checkboxes.fadeOut(200, function () {	
			$(this).fadeIn(200);
		});
	},
	/**
	 * @param {JQuery<HTMLElement>} $checkbox
	 * @param {GroupSelector}
	 */
	checkboxClick($checkbox, groupSelector) {
		const { selectedIds } = groupSelector;
		const nodeId = $checkbox.attr("data-node-id");
		const index = selectedIds.indexOf(nodeId);
		if (index > -1) {
			iconTogglers.disableCheck($checkbox);
			selectedIds.splice(index, 1);
		} else {
			iconTogglers.enableCheck($checkbox);
			selectedIds.push(nodeId);
		}
	},
	/**
	 * @param {GroupSelector} groupSelector
	 */
	selectAllClick(groupSelector) {
		const { selectedIds, visibleIds } = groupSelector;
		if (visibleIds.length === selectedIds.length) {
			groupSelector.uncheckAll();
			groupSelector.resetSelection(visibleIds);
		} else {
			groupSelector.checkAll();
			groupSelector.buildSelection(visibleIds);
		}
		eventHandlers.updateCounter(groupSelector);
	},
	/**
	 * @param {JQuery<HTMLElement>} $pageBtn
	 * @param {GroupSelector} groupSelector
	 */
	onPageClick($pageBtn, groupSelector) {
		$pageBtn
			.addClass("animated")
			.one("animationend", function () {
				$(this).removeClass("animated");
			});
		const direction = $pageBtn.attr("data-action");
		groupSelector.changePage(direction);
	},
};

const iconTogglers = {
	disableCheck($checkbox) {
		const { checkbox } = assetIcons;
		$checkbox
			.removeClass("active")
			.find(".checkbox-icon")
			.removeClass(checkbox.on)
			.addClass(checkbox.off);
	},
	enableCheck($checkbox) {
		const { checkbox } = assetIcons;
		$checkbox
			.addClass("active")
			.find(".checkbox-icon")
			.removeClass(checkbox.off)
			.addClass(checkbox.on);
	},
	selectAllOn($selectAll) {
		const { selectAll } = assetIcons;
		$selectAll
			.addClass("active")
			.find(".select-all-icon")
			.removeClass(selectAll.off)
			.addClass(selectAll.on);
	},
	selectAllOff($selectAll) {
		const { selectAll } = assetIcons;
		$selectAll
			.removeClass("active")
			.find(".select-all-icon")
			.removeClass(selectAll.on)
			.addClass(selectAll.off);
	},
};

class Pager {
	constructor(pageSize = 20) {
		this.pageSize = pageSize;
		this.totalPages = 0;
		this._index = 0;
	}
	init(pageData) {
		this.totalPages = Math.ceil(pageData.length / this.pageSize);
		this._index = 0;
	}
	getPageContent(pageData) {
		const start = this.index * this.pageSize;
		const end = Math.min(start + this.pageSize, pageData.length);
		return pageData.slice(start, end);
	}
	/**
	 * @param {number} index
	 */
	set index(index) {
		if (index < 0) {
			this._index = this.totalPages - 1;
		} else if (index >= this.totalPages) {
			this._index = 0;
		} else {
			this._index = index;
		}
	}
	get index() {
		return this._index;
	}
}
