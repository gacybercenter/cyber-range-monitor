
/* 
  WORK IN PROGRESS
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

// testing related
// const demoSpecific = {
// 	coinFlip(heads, tails) {
// 		return Math.random() < 0.5 ? heads : tails;
// 	},
// 	createSampleData(amount) {
// 		const data = [];
// 		for (let i = 0; i < amount; i++) {
// 			data.push(demoSpecific.nodeFactory(i));
// 		}
// 		return data;
// 	},
// 	nodeFactory(nodeI) {
// 		return {
// 			name: `Node ${nodeI + 1}`,
// 			active: demoSpecific.coinFlip(true, false),
// 			id: nodeI,
// 			os: demoSpecific.coinFlip("win", "linux"),
// 			isActive() {
// 				return this.active;
// 			},
// 			getOsIcon() {
// 				return assetIcons.osIcons[this.os];
// 			},
// 		};
// 	},
// };

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

function configCheckbox($checkbox, connection) {
	$checkbox
		.attr("data-node-id", connection.id) // change to identifier later
		.attr("data-active", connection.isActive())
		.find(".checkbox-label")
		.text(connection.name)
		.append(`<i class="node-os-icon ${connection.getOsIcon()}"></i>`);
}

const assetFactory = {
	createCheckbox(connection) {
		const $checkbox = components.cloneAsset(assets.checkbox);
		configCheckbox($checkbox, connection);
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
		$(".pager-label").text(`${index + 1} / ${totalPages}`);
	}
}

const refreshCheckbox = ($checkbox, pageData, cur) => {
	$checkbox.fadeOut(200, function () {
		if (cur > pageData.length - 1) {
			return;
		}
		configCheckbox($(this), pageData[cur]);
		$(this).fadeIn(200);
	});
};

class GroupSelector {
	constructor() {
		this.renderedItems = [];
		this.dataSet = [];
		this.pager = null;
		this.$content = null;
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
				$filter.addClass(assetIcons.on);
			}
			$filters.append($filter);
		});
		const page = components.cloneAsset(assets.pager);
		this.$content.find(".pagination-container").append(page);
	}

	renderPage(selectedIds) {
		if (this.pager.totalPages === 1) {
			this.$content.find(".pagination-container").hide();
		} else {
			this.$content.find(".pagination-container").show();
		}

		const pageData = this.pager.getPageContent(this.renderedItems);
		const $checkboxes = this.$content.find(".checkbox-container");
		$checkboxes.empty();
		pageData.forEach((connection) => {
			const $checkbox = assetFactory.createCheckbox(connection);
			if (selectedIds.includes(connection.id)) {
				iconTogglers.enableCheck($checkbox);
			}
			$checkboxes.append($checkbox);
		});
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
			case assetIcons.on:
				this.renderedItems = this.dataSet.filter((n) => n.isActive());
				break;

			case "inactive":
				this.renderedItems = this.dataSet.filter((n) => !n.isActive());
				break;

			default:
				this.renderedItems = this.dataSet;
				break;
		}
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
		const allChecked = selectedCount === this.dataSet.length;
		iconTogglers.selectAllToggler(allChecked);
		if (allChecked && !$counter.hasClass("reached")) {
			$counter.addClass("reached");
		} else if (!allChecked && $counter.hasClass("reached")) {
			$counter.removeClass("reached");
		}
	}
}

const assetManager = {
	renderedItems: [],
	dataSet: [],
	pager: null,
	$content: null,
	init(connections) {
		const $contentContainer = components.cloneAsset(assets.container);
		this.dataSet = connections;
		this.renderedItems = connections;
		this.pager = new Pager();
		this.pager.init(connections);
		this.$content = $contentContainer;
		return $contentContainer;
	},
	/**
	 *
	 * @param {Object} filterConfigs
	 * @param {string[]} selectedIds
	 * @returns {void}
	 */
	renderComponents(filterConfigs, selectedIds) {
		const $filters = this.$content.find(".filters");
		filterConfigs.forEach((filterConfig) => {
			const $filter = assetFactory.createFilter(filterConfig);
			if (filterConfig.text === "All") {
				$filter.addClass(assetIcons.on);
			}
			$filters.append($filter);
		});
		const page = components.cloneAsset(assets.pager);
		this.$content.find(".pagination-container").append(page);
		this.renderPage(selectedIds);
	},
	/**
	 *
	 * @param {string[]} selectedIds
	 */
	renderPage(selectedIds) {
		const pageData = this.pager.getPageContent(this.renderedItems);
		const $checkboxes = this.$content.find(".checkbox-container");
		$checkboxes.empty();
		pageData.forEach((connection) => {
			const $checkbox = assetFactory.createCheckbox(connection);
			if (selectedIds.includes(connection.id)) {
				iconTogglers.enableCheck($checkbox);
			}
			$checkboxes.append($checkbox);
		});
		Pager.updateText(this.pager);
	},
	/**
	 *
	 * @param {string} action
	 * @param {string[]} selectedIds
	 */
	changePage(direction, selectedIds) {
		if (direction === "left") {
			this.pager.index--;
		} else {
			this.pager.index++;
		}
		this.renderPage(selectedIds);
	},
	/**
	 * @param {string} newFilter
	 * @param {string[]} selectedIds
	 */
	changeFilter(newFilter, selectedIds) {
		switch (newFilter) {
			case assetIcons.on:
				this.renderedItems = this.dataSet.filter((n) => n.isActive());
				break;

			case "inactive":
				this.renderedItems = this.dataSet.filter((n) => !n.isActive());
				break;

			default:
				this.renderedItems = this.dataSet;
				break;
		}
		this.pager.init(this.renderedItems);
		console.debug(
			`[INFO] - Filtered items: ${this.renderedItems.length} / ${this.dataSet.length}`
		);
		Pager.updateText(this.pager);
		this.renderPage(selectedIds);
	},
	/**
	 * @param {number} selectedCount
	 */
	updateCounter(selectedCount) {
		const $counter = $("#selectedCounter");
		$counter.text(selectedCount);
		const allChecked = selectedCount === this.dataSet.length;
		iconTogglers.selectAllToggler(allChecked);
		if (allChecked && !$counter.hasClass("reached")) {
			$counter.addClass("reached");
		} else if (!allChecked && $counter.hasClass("reached")) {
			$counter.removeClass("reached");
		}
	},
};

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
			.addClass(assetIcons.on)
			.find(".select-all-icon")
			.removeClass(selectAll.off)
			.addClass(selectAll.on);
	},
	selectAllOff($selectAll) {
		const { selectAll } = assetIcons;
		$selectAll
			.removeClass(assetIcons.on)
			.find(".select-all-icon")
			.removeClass(selectAll.off)
			.addClass(selectAll.on);
	},
	selectAllToggler(allChecked) {
		const $selectAll = $(".select-all");
		if (allChecked && !$selectAll.hasClass(assetIcons.on)) {
			iconTogglers.selectAllOn($selectAll);
		} else if (!allChecked && $selectAll.hasClass(assetIcons.on)) {
			iconTogglers.selectAllOff($selectAll);
		}
	},
};

function demo() {
	$(function () {
		const selectedIds = [];
		const nodes = demoSpecific.createSampleData(15);
		const activeCount = nodes.filter((n) => n.isActive()).length || 0;
		const filterConfigs = [
			{
				text: "All",
				count: nodes.length,
				icon: assetIcons.filterIcons.all,
				dataFilter: "all",
			},
			{
				text: "Inactive",
				count: nodes.length - activeCount,
				icon: assetIcons.filterIcons.inactive,
				dataFilter: "inactive",
			},
			{
				text: assetIcons.on,
				count: activeCount,
				icon: assetIcons.filterIcons.active,
				dataFilter: assetIcons.on,
			},
		];

		const $content = assetManager.init(nodes);
		$("body").append($content);
		assetManager.renderComponents(filterConfigs, selectedIds);

		$content.on("click", ".filter-button", function () {
			const newFilter = $(this).attr("data-filter");
			const tagFilter = assetManager.changeFilter(newFilter, selectedIds);
			$(this).addClass(assetIcons.on).siblings().removeClass(assetIcons.on);
			const $checkboxes = $(".checkbox");
			if (!tagFilter) {
				$checkboxes.fadeOut(200, function () {
					$(this).fadeIn(200);
				});
			} else {
				$checkboxes.not(tagFilter).fadeOut(200, function () {
					$checkboxes.filter(tagFilter).fadeIn(200);
				});
			}
		});

		$content.on("click", ".checkbox", function () {
			const nodeId = $(this).attr("data-node-id");
			const index = selectedIds.indexOf(nodeId);
			const isChecked = index > -1;
			if (isChecked) {
				iconTogglers.disableCheck($(this));
				selectedIds.splice(index, 1);
			} else {
				iconTogglers.enableCheck($(this));
				selectedIds.push(nodeId);
			}
			console.debug("[INFO] - Selected IDs -> ", selectedIds);
			assetManager.updateCounter(selectedIds.length);
		});

		$content.on("click", ".select-all", function () {
			if ($(this).hasClass(assetIcons.on)) {
				$(".checkbox").each(function () {
					iconTogglers.disableCheck($(this));
				});
				selectedIds.length = 0;
				assetManager.updateCounter(selectedIds.length);
				console.debug("[INFO] - Selected IDs -> ", selectedIds);
				return;
			}
			$(this).addClass(assetIcons.on);
			$(".checkbox")
				.not(".active")
				.each(function () {
					const nodeId = $(this).attr("data-node-id");
					selectedIds.push(nodeId);
					iconTogglers.enableCheck($(this));
				});
			assetManager.updateCounter(selectedIds.length, nodes);
			console.debug("[INFO] - Selected IDs -> ", selectedIds);
		});

		$content.on("click", ".page-button", function () {
			const direction = $(this).attr("data-action");
			console.debug("[INFO] - Page Change, going -> ", direction);
			assetManager.changePage(direction, selectedIds);
		});
	});
}
