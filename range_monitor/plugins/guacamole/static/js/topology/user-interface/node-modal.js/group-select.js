



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
 * @param {ConnectionNode[]} childConnections 
 * @returns {JQuery<HTMLElement>}
 */
export function renderGroupSelector(selectedIds, childConnections) {
	const assetManager = new GroupSelector();
	const $content = assetManager.init(childConnections);

	const filterConfigs = getFilterConfigs(childConnections);
	assetManager.renderComponents(filterConfigs);
	assetManager.renderPage(selectedIds);
	addGroupSelectEvents($content, selectedIds, assetManager);
	
	return $content;
}

function addGroupSelectEvents($content, selectedIds, assetManager) {
	$content.on("click", ".filter-button", function () {
		assetManager.filterClick($(this), selectedIds);
	});

	$content.on("click", ".checkbox", function () {
		assetManager.checkboxClick($(this), selectedIds);
		assetManager.updateCounter(selectedIds.length);
	});

	$content.on("click", ".select-all", function () {
		assetManager.selectAllClick(selectedIds);
	});

	$content.on("click", ".pager-icon", function () {
		$(this).addClass("animated").one("animationend", function () {
			$(this).removeClass("animated");
		});
		const direction = $(this).attr("data-action");
		assetManager.changePage(direction, selectedIds);
	});
}

const getFilterConfigs = (childConnections) => {
	/* 
		below are all of the filters I've added &
		set up for "Group Selection", feel free to 
		add your own however, try do so without changing
		the existing design.
	*/
	const { filterIcons } = assetIcons;
	const activeConnections = childConnections
		.filter(n => n.isActive()) || [];

	const showAllFilter = {
		text: "All",
		count: childConnections.length,
		icon: filterIcons.all,
		dataFilter: "all",
	};
	const inactiveFilter = 	{
		text: "Inactive",
		count: childConnections.length - activeConnections.length,
		icon: filterIcons.inactive,
		dataFilter: "inactive",
	};
	const activeFilter =	{
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
 * @property {ConnectionNode[]} renderedItems - the "filtered" items, (e.g the active filter would make it store all active connections)
 * @property {ConnectionNode[]} childConnections - all Child ConnectionNodes of the Group, does not change.
 * @property {Pager} pager - the pager object for the Group Selector, handles logic for paging.
 */
class GroupSelector {
	constructor() {
		this.renderedItems = [];
		this.childConnections = [];
		this.pager = null;
		this.$content = null;
	}

	/**
	 * @param {Array} connections
	 * @returns {JQuery<HTMLElement}
	 */
	init(connections) {
		const $contentContainer = components.cloneAsset(assets.container);
		this.childConnections = connections;
		this.renderedItems = connections;
		this.pager = new Pager();
		this.pager.init(connections);
		this.$content = $contentContainer;
		return $contentContainer;
	}
	/**
	 *
	 * @param {Object} filterConfigs
	 * @returns {Object{ $checkboxes, $filters, $selectAll }}
	 */
	renderComponents(filterConfigs) {
		this.renderFilters(filterConfigs);
		const page = components.cloneAsset(assets.pager);
		this.$content.find(".pagination-container").append(page);
	}
	/**
	 * @param {object[]} filterConfigs - { text: string, count: number, icon: string, dataFilter: string }
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
		if($tag.length === 0) {
			console.warn(`[WARN] - Group Selector Tag not found: ${selector}`);
		}
		return $tag;
	}

	/**
	 * Renders a single page of the Group Selector,
	 * paging is handled by the Pager class.
	 * @param {string[]} selectedIds 
	 */
	renderPage(selectedIds) {
		const pageContents = this.pager.getPageContent(this.renderedItems);
		const $checkboxes = this.findTag(".checkbox-container");
		$checkboxes.empty();
		this.pager.buildPage(pageContents, selectedIds, $checkboxes);
	}

	/**
	 * Changes the page of the Group Selector,
	 * actions are from the "data-action" attribute
	 * of a page icon page and is passed by caller
	 * @param {string} action
	 * @param {string[]} selectedIds
	 */
	changePage(action, selectedIds) {
		console.debug("[INFO] - Going -> ", action);

		// note, pager handles indexing in setter
		if (action === "left") {
			this.pager.index--;
		} else if(action === "right") {
			this.pager.index++;
		} else {
			console.warn(`[NOTE] - Invalid Page Action: ${action}`);
		}

		this.renderPage(selectedIds);
	}
	/**
	 *
	 * @param {string} newFilter
	 * @param {string[]} selectedIds
	 */
	changeFilter(newFilter, selectedIds) {
		if(newFilter === "active") {
			this.renderedItems = this.childConnections.filter(n => n.isActive());
		} else if(newFilter === "inactive") {
			this.renderedItems = this.childConnections.filter(n => !n.isActive());			
		} else {
			this.renderedItems = this.childConnections;
		}
		this.pager.init(this.renderedItems);
		Pager.updateText(this.pager);
		this.renderPage(selectedIds);
	}

	/**
	 * @param {number} selectedCount
	 */
	updateCounter(selectedCount) {
		const allChecked = selectedCount === this.pager.pageSize;
		
		const $selectAll = this.findTag(".select-all");
		if(allChecked && !$selectAll.hasClass("active")) {
			iconTogglers.selectAllOn($(".select-all"));
		} else if(!allChecked && $selectAll.hasClass("active")) {
			iconTogglers.selectAllOff($selectAll);
		}

		const $counter = this.findTag("#selectedCounter");
		$counter.text(selectedCount);
		if (allChecked && !$counter.hasClass("reached")) {
			$counter.addClass("reached");
		} else if (!allChecked && $counter.hasClass("reached")) {
			$counter.removeClass("reached");
		}
	}
	uncheckAll() {
		this.$content.find(".checkbox").each(function () {
			iconTogglers.disableCheck($(this));
		});
	}
	/**
	 * @param {string[]} selectedIds 
	 */
	checkAll(selectedIds) {
		this.$content.find(".checkbox")
			.not(".active")
			.each(function () {
				const nodeId = $(this).attr("data-node-id");
				if(!selectedIds.includes(nodeId)) {
					iconTogglers.enableCheck($(this));
				}
			});
	}
	/**
	 * maps all of the current filtered items to their ids 
	 * @returns {string[]}
	 */
	getVisibleIds() {
		return this.renderedItems.map((n) => n.id);
	}

	checkboxClick($checkbox, selectedIds) {
		const nodeId = $checkbox.attr("data-node-id");
		const index = selectedIds.indexOf(nodeId);
		if (index > -1) {
			iconTogglers.disableCheck($checkbox);
			selectedIds.splice(index, 1);
		} else {
			iconTogglers.enableCheck($checkbox);
			selectedIds.push(nodeId);
		}
	}

	selectAllClick(selectedIds) {
		const available = this.getVisibleIds();
		if (available.length === selectedIds.length) {
			this.uncheckAll();
			selectedIds = selectedIds.filter((id) => !available.includes(id));
		} else {
			this.checkAll(selectedIds);
			selectedIds = [...new Set([...selectedIds, ...available])];		
		}
		this.updateCounter(selectedIds.length);
	}

	filterClick($filterBtn, selectedIds) {
		const newFilter = $filterBtn.attr("data-filter");
		this.changeFilter(newFilter, selectedIds);
		$filterBtn
			.addClass(assetIcons.on)
			.siblings()
			.removeClass(assetIcons.on);
		$(".checkbox").fadeOut(200, function () {
			$(this).fadeIn(200);
		});
	}


}

class Pager {
	constructor(pageSize = 20) {
		this.pageSize = pageSize;
		this.totalPages = 0;
		this._index = 0;
	}
	init(childConnections) {
		this.totalPages = Math.ceil(childConnections.length / this.pageSize);
		this._index = 0;
	}
	getPageContent(childConnections) {
		const start = this.index * this.pageSize;
		const end = Math.min(start + this.pageSize, childConnections.length);
		return childConnections.slice(start, end);
	}
	/**
	 * @param {number} index
	 * @description handles the logic for the pager index and "bounces" it
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
	
	static updateText(pager) {
		const { index, totalPages } = pager;
		$(".pager-label").text(`Page ${index + 1} / ${totalPages}`);
	}

	/**
	 * @param {Object[]} pageContents 
	 * @param {string[]} selectedIds 
	 * @param {JQuery<HTMLElement>} $pageHolder 
	 */
	buildPage(pageContents, selectedIds, $pageHolder) {
		pageContents.forEach(connection => {
			const $checkbox = components.createCheckbox(connection);
			$pageHolder.append($checkbox);
			if(selectedIds.includes(connection.identifier)) {
				iconTogglers.enableCheck($checkbox);
				$checkbox.addClass("active");
			}
		});
		Pager.updateText(this.pager);
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
			.removeClass(assetIcons.on)
			.find(".checkbox-icon")
			.removeClass(checkbox.on)
			.addClass(checkbox.off);
	},

	enableCheck($checkbox) {
		const { checkbox } = assetIcons;
		$checkbox
			.addClass(assetIcons.on)
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
 * for commonly rendered assets 
 */
const components = {
	assets: {},
	cloneAsset(templateId) {
		if (!this.assets[templateId]) {
			this.registerAsset(templateId);
		}
		return this.assets[templateId].clone();
	},
	registerAsset(templateId) {
		const template = document.getElementById(templateId);
		if (!template) {
			throw new Error(`Template with id ${templateId} not found`);
		}
		const cloned = template.content.cloneNode(true).children[0];
		this.assets[templateId] = $(cloned);
	},
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

	createFilter(filterConfig) {
		const { text, count, icon, dataFilter } = filterConfig;
		const $filter = components.cloneAsset(assets.filter);
		console.debug("[INFO] - Filters: ", $filter);
		$filter
			.attr("data-filter", dataFilter)
			.find(".filter-label")
			.prepend(`${text} (${count}) `)
			.find(".filter-icon")
			.addClass(icon);
		return $filter;
	},
};