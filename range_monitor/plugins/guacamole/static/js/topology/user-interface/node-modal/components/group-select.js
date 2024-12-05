/**
 * @enum {string}
 * @description contains all the icons used in the Group Selector
 * bc if I forget that fas class names, so will you =)
 */
const assetIcons = {
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
};

/**
 * renders the group selector & adds the necessary event handlers
 * @param {string[]} selectedIds
 * @param {ConnectionNode[]} pageData
 * @returns {Object} - { $content, groupSelector }
 */
export function renderGroupSelector(pageData) {
	const groupSelector = new GroupSelector();
	const filterConfigs = getFilterConfigs(pageData);
	const $content = groupSelector.init(pageData, filterConfigs);

	groupSelector.renderPage();

	addGroupSelectEvents($content, groupSelector);
	return { $content, groupSelector };
}

/**
 *
 * @param {JQuery<HTMLElement>} $content
 * @param {string[]} selectedIds
 * @param {GroupSelector} groupSelector
 */
function addGroupSelectEvents($content, groupSelector) {
	$content.on("click", ".filter-button", function () {
		eventHandlers.filterClick($(this), groupSelector);
	});

	$content.on("click", ".checkbox", function () {
		eventHandlers.checkboxClick($(this), groupSelector);
		eventHandlers.updateCounter(groupSelector);
	});

	$content.on("click", ".select-all", () => {
		eventHandlers.selectAllClick(groupSelector);
		console.log("[INFO] selectedIDs after click -> ");
	});

	$content.on("click", ".pager-icon", function () {
		eventHandlers.onPageClick($(this), groupSelector);
	});
}

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
	constructor() {
		this.filteredItems = [];
		this.pageData = [];
		this.pager = null;
		this.$content = null;
		this.selectedIds = [];
	}

	/**
	 * @param {Array} connections
	 * @param {import("./template-assets").FilterConfig[]} filterConfigs
	 * @returns {JQuery<HTMLElement>}
	 */
	init(connections, filterConfigs) {
		const $contentContainer = components.cloneAsset(assets.container);
		this.pageData = connections;
		this.filteredItems = connections;
		this.pager = new Pager(12);
		this.pager.init(connections);
		this.$content = $contentContainer;
		this.renderFilters(filterConfigs);
		const page = components.cloneAsset(assets.pager);
		this.$content.find(".pagination-container").append(page);
		return $contentContainer;
	}

	/**
	 * maps all of the current filtered items to their ids
	 * @returns {string[]}
	 */
	get visibleIds() {
		return this.filteredItems.map((n) => n.identifier);
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
	 * @param {import("./template-assets").FilterConfig[]} filterConfigs - { text: string, count: number, icon: string, dataFilter: string }
	 */
	renderFilters(filterConfigs) {
		const $filters = this.findTag(".filters");
		filterConfigs.forEach((filterConfig) => {
			const $filter = components.createFilter(filterConfig);
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
			console.warn(`[WARN] - Group Selector Tag not found: ${selector}`);
		}
		return $tag;
	}
	renderPage() {
		const pageContents = this.pager.getPageContent(this.filteredItems);
		const $checkboxHolder = this.findTag(".checkbox-container");
		$checkboxHolder.empty();
		pageContents.forEach((connection) => {
			const { identifier } = connection;
			const $checkbox = components.createCheckbox(connection);
			if (this.selectedIds.includes(identifier)) {
				iconTogglers.enableCheck($checkbox);
				$checkbox.addClass("active");
			}
			$checkboxHolder.append($checkbox);
		});

		const $pageIcons = this.findTag(".pager-icon");
		if (this.pager.totalPages > 1) {
			$pageIcons.prop("disabled", false);
		} else {
			$pageIcons.prop("disabled", true);
		}
		this.updatePageInfo();
		eventHandlers.updateCounter(this);
	}
	updatePageInfo() {
		const { index, totalPages } = this.pager;
		this.findTag(".pager-label").text(`Page ( ${index + 1} / ${totalPages} ) `);
	}

	/**
	 * @param {string} action
	 * @param {string[]} selectedIds
	 */
	changePage(action) {
		console.log("[INFO] - Going -> ", action);
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
		if (newFilter === "active") {
			this.filteredItems = this.pageData.filter((n) => n.isActive());
		} else if (newFilter === "inactive") {
			this.filteredItems = this.pageData.filter((n) => !n.isActive());
		} else {
			this.filteredItems.length = 0;
			this.filteredItems.push(...this.pageData);
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

		const allChecked = (selectedIds.length === filteredItems.length);

		const $selectAll = groupSelector.findTag(".select-all");
		if (allChecked && !$selectAll.hasClass("active")) {
			iconTogglers.selectAllOn($selectAll);
		} else if (!allChecked && $selectAll.hasClass("active")) {
			iconTogglers.selectAllOff($selectAll);
		}

		const $counter = groupSelector.findTag("#selectedCounter");
		if (allChecked && !$counter.hasClass("reached")) {
			$counter.addClass("reached");
		} else if (!allChecked && $counter.hasClass("reached")) {
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

		$filterBtn.addClass("active").siblings().removeClass(assetIcons.on);

		groupSelector.checkboxes.fadeOut(200, function () {
			$(this).fadeIn(200);
		});
	},
	/**
	 * @param {JQuery<HTMLElement>} $checkbox
	 * @param {GroupSelector}
	 */
	checkboxClick($checkbox, { selectedIds }) {
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
		$pageBtn.addClass("animated").one("animationend", function () {
			$(this).removeClass("animated");
		});
		const direction = $pageBtn.attr("data-action");
		groupSelector.changePage(direction);
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

const iconTogglers = {
	toggleCheckbox($checkbox, condition) {
		if (condition) {
			iconTogglers.enableCheck($checkbox);
		} else {
			iconTogglers.disableCheck($checkbox);
		}
	},

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

/**
 * @enum {string} - ids of the template tags
 */
const assets = {
	checkbox: "modalCheckbox",
	filter: "filterTab",
	pager: "checkboxPager",
	container: "groupSelect",
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
			throw new Error(`Template with id ${templateId} not found`);
		}
		const cloned = template.content.cloneNode(true).children[0];
		this.assets[templateId] = $(cloned);
	},
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
	 * @param {Object} filterConfig
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
};

const getFilterConfigs = (pageData) => {
	/* 
		below are all of the filters I've added &
		set up for "Group Selection", feel free to 
		add your own however, try do so without changing
		the existing design.
	*/
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
