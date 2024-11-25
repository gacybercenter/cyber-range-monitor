const appIcons = {
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
	osIcons: {
		win: "fa-brands fa-windows",
		linux: "fa-brands fa-linux",
	},
	filterIcons: {
		all: "fa-solid fa-users-rays",
		inactive: "fa-solid fa-power-off",
		active: "fa-solid fa-signal",
	},
	on: "active",
};

const demoSpecific = {
	coinFlip(heads, tails) {
		return Math.random() < 0.5 ? heads : tails;
	},
	createSampleData(amount) {
		const data = [];
		for (let i = 0; i < amount; i++) {
			data.push(demoSpecific.nodeFactory(i));
		}
		return data;
	},
	nodeFactory(nodeI) {
		return {
			name: `Node ${nodeI + 1}`,
			active: demoSpecific.coinFlip(true, false),
			id: `${nodeI + 1}`,
			os: demoSpecific.coinFlip("win", "linux"),
			isActive() {
				return this.active;
			},
			getOsIcon() {
				return appIcons.osIcons[this.os];
			},
		};
	},
};

const assets = {
	checkbox: "modalCheckbox",
	filter: "filterTab",
	pager: "checkboxPager",
	container: "groupSelect",
};

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
};

const assetFactory = {
	createCheckbox(connection) {
		const $checkbox = components.cloneAsset(assets.checkbox);
		$checkbox
			.attr("data-node-id", connection.id) 
			.attr("data-active", connection.isActive())
			.find(".checkbox-label")
			.text(connection.name)
			.append(` <i class="node-os-icon ${connection.getOsIcon()}"></i>`);
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

class Pager {
	constructor(pageSize = 20) {
		this.pageSize = pageSize;
		this.totalPages = 0;
		this._index = 0;
	}
	init(dataSet) {
		this.totalPages = Math.ceil(dataSet.length / this.pageSize);
		this._index = 0;
	}
	getPageContent(dataSet) {
		const start = this.index * this.pageSize;
		const end = Math.min(start + this.pageSize, dataSet.length);
		return dataSet.slice(start, end);
	}
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
}

class GroupSelector {
	constructor() {
		this.renderedItems = [];
		this.dataSet = [];
		this.pager = null;
		this.$content = null;
		this.currentFilter = "all";
	}

	/**
	 * @param {Array} connections
	 * @returns {JQuery<HTMLElement}
	 */
	init(connections) {
		const $contentContainer = components.cloneAsset(assets.container);
		this.dataSet = connections;
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
		const $filters = this.$content.find(".filters");
		filterConfigs.forEach((filterConfig) => {
			const $filter = assetFactory.createFilter(filterConfig);
			if (filterConfig.text === "All") {
				$filter.addClass(appIcons.on);
			}
			$filters.append($filter);
		});
		const page = components.cloneAsset(assets.pager);
		this.$content.find(".pagination-container").append(page);
	}

	renderPage(selectedIds) {
		const pageData = this.pager.getPageContent(this.renderedItems);
		const $checkboxes = this.$content.find(".checkbox-container");
		$checkboxes.empty();
		pageData.forEach((connection) => {
			const $checkbox = assetFactory.createCheckbox(connection);
			$checkboxes.append($checkbox);
			const shouldCheck = selectedIds.includes(connection.id);
			console.log(`[INFO] - Should Check ${connection.id} -> `, shouldCheck);
			if(shouldCheck) {
				iconTogglers.enableCheck($checkbox);
				$checkbox.addClass("active");
			}
		});
		console.log("Selected IDs -> ", selectedIds);
		Pager.updateText(this.pager);
	}

	/**
	 * @param {string} action
	 * @param {string[]} selectedIds
	 */
	changePage(action, selectedIds) {
		if (action === "left") this.pager.index--;
		
		else this.pager.index++;

		this.renderPage(selectedIds);
	}
	/**
	 *
	 * @param {string} newFilter
	 * @param {string[]} selectedIds
	 */
	changeFilter(newFilter, selectedIds) {
		switch (newFilter) {
			case "active":
				this.renderedItems = this.dataSet.filter((n) => n.isActive());
				break;

			case "inactive":
				this.renderedItems = this.dataSet.filter((n) => !n.isActive());
				break;

			default:
				this.renderedItems = this.dataSet;
				break;
		}
		this.currentFilter = newFilter;
		this.pager.init(this.renderedItems);
		Pager.updateText(this.pager);
		this.renderPage(selectedIds);
	}
	/**
	 *
	 * @param {number} selectedCount
	 */
	updateCounter(selectedCount) {
		const $counter = $("#selectedCounter");
		$counter.text(selectedCount);
		const allChecked = selectedCount === this.pager.pageSize;
		const $selectAll = $(".select-all");
		if(allChecked && !$selectAll.hasClass("active")) {
			iconTogglers.selectAllOn($(".select-all"));
		} else if(!allChecked && $selectAll.hasClass("active")) {
			iconTogglers.selectAllOff($selectAll);
		}

		if (allChecked && !$counter.hasClass("reached")) {
			$counter.addClass("reached");
		} else if (!allChecked && $counter.hasClass("reached")) {
			$counter.removeClass("reached");
		}
	}
	getVisibleIds() {
		return this.renderedItems.map((n) => n.id);
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
		const { checkbox } = appIcons;
		$checkbox
			.removeClass(appIcons.on)
			.find(".checkbox-icon")
			.removeClass(checkbox.on)
			.addClass(checkbox.off);
	},

	enableCheck($checkbox) {
		const { checkbox } = appIcons;
		$checkbox
			.addClass(appIcons.on)
			.find(".checkbox-icon")
			.removeClass(checkbox.off)
			.addClass(checkbox.on);
	},

	selectAllOn($selectAll) {
		const { selectAll } = appIcons;
		$selectAll
			.addClass("active")
			.find(".select-all-icon")
			.removeClass(selectAll.off)
			.addClass(selectAll.on);
	},

	selectAllOff($selectAll) {
		const { selectAll } = appIcons;
		$selectAll
			.removeClass("active")
			.find(".select-all-icon")
			.removeClass(selectAll.on)
			.addClass(selectAll.off);
	},
	
	selectAllToggler(allChecked) {
		const $selectAll = $(".select-all");
		console.log("All Checked -> ", allChecked);
		if (allChecked) {
			iconTogglers.selectAllOn($selectAll);
		} else if (!allChecked) {
			iconTogglers.selectAllOff($selectAll);
		}
	},

};

const eventHandlers = {
	filterClick($filterBtn, assetManager, selectedIds) {
		const newFilter = $filterBtn.attr("data-filter");
		assetManager.changeFilter(newFilter, selectedIds);
		$filterBtn
			.addClass(appIcons.on)
			.siblings()
			.removeClass(appIcons.on);
		$(".checkbox").fadeOut(200, function () {
			$(this).fadeIn(200);
		});
	},

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
	},
};



const checkboxUtils = {
	uncheckAll() {
		$(".checkbox").each(function () {
			iconTogglers.disableCheck($(this));
		});
	},
	checkAll(selectedIds) {
		$(".checkbox")
			.not(".active")
			.each(function () {
				const nodeId = $(this).attr("data-node-id");
				if(!selectedIds.includes(nodeId)) {
					iconTogglers.enableCheck($(this));
				}
			});
	}
};






// $(function () {
// 	let selectedIds = [];
// 	const nodes = demoSpecific.createSampleData(45);
// 	const activeCount = nodes.filter((n) => n.isActive()).length || 0;
// 	const filterConfigs = [
// 		{
// 			text: "All",
// 			count: nodes.length,
// 			icon: appIcons.filterIcons.all,
// 			dataFilter: "all",
// 		},
// 		{
// 			text: "Inactive",
// 			count: nodes.length - activeCount,
// 			icon: appIcons.filterIcons.inactive,
// 			dataFilter: "inactive",
// 		},
// 		{
// 			text: appIcons.on,
// 			count: activeCount,
// 			icon: appIcons.filterIcons.active,
// 			dataFilter: appIcons.on,
// 		},
// 	];
// 	const assetManager = new GroupSelector();
// 	const $content = assetManager.init(nodes);
// 	assetManager.renderComponents(filterConfigs, selectedIds);
// 	assetManager.renderPage(selectedIds);

// 	$("body").append($content);

// 	$content.on("click", ".filter-button", function () {
// 		eventHandlers.filterClick($(this), assetManager, selectedIds);
// 	});

// 	$content.on("click", ".checkbox", function () {
// 		eventHandlers.checkboxClick($(this), selectedIds);
// 		assetManager.updateCounter(selectedIds.length);
// 	});

// 	$content.on("click", ".select-all", function () {
// 		const available = assetManager.getVisibleIds();
// 		if (available.length === selectedIds.length) {
// 			checkboxUtils.uncheckAll(selectedIds);
// 			selectedIds = selectedIds.filter((id) => !available.includes(id));
// 		} else {
// 			checkboxUtils.checkAll(selectedIds);
// 			selectedIds = [...new Set([...selectedIds, ...available])];		
// 		}
// 		assetManager.updateCounter(selectedIds.length);
// 	});

// 	$content.on("click", ".pager-icon", function () {
// 		$(this).addClass("animated").one("animationend", function () {
// 			$(this).removeClass("animated");
// 		});
// 		const direction = $(this).attr("data-action");
// 		assetManager.changePage(direction, selectedIds);
// 	});
// });
