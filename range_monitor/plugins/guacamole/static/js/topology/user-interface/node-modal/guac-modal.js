// topology/user-interface/node-modal/guac-modal.js
/**
 * @enum {string}
 * saves time when refactoring
 */
const modalTags = {
	overlay: "#modalOverlay",
	body: "#modalBody",
	title: "#modalTitle",
	closeBtn: ".close-btn",
	tabs: "#tabWindows",
	content: ".tab-content-container",
};

const modalEvents = {
	handleCollapse(event) {
		const $header = $(event.currentTarget);
		const $content = $header.next(".collapsible-content");
		const $icon = $header.find(".collapse-toggle");

		const isExpanded = $header.attr("aria-expanded") === "true";

		const collapsed = $icon.attr("data-collapsed-icon");
		const expanded = $icon.attr("data-expanded-icon");
		
		$icon.fadeOut(100, () => {
			$icon.fadeIn(100, function () {
				$(this)
				.removeClass(isExpanded ? expanded : collapsed)
				.addClass(isExpanded ? collapsed : expanded);
			});
		});
		$header.attr("aria-expanded", !isExpanded);
		$content.toggleClass("expanded");
	},
	fadeInModal(modal) {
		const { $overlay, $windowTabs, $modalContent } = modal;
		const activateFirst = ($tag, selector) => {
			return $tag
				.find(selector)
				.eq(0)
				.addClass("active")
				.attr("aria-selected", "true");
		};
		$overlay.fadeIn(200, () => {
			activateFirst($windowTabs, ".tab").focus();
			activateFirst($modalContent, ".tab-content").show();
			$(document).on("keydown", modal.onKeyDown);
		});
	},
};
/**
 * @class Modal
 * @summary
 * dynamically generates HTML for a modal for the connection nodes & groups and the
 * settings of the topology with tabs for each section. it uses a single piece of HTML 
 * to generate this which can be seen in "topology.html" and by leveraging the use of 
 * template tags; common components are cached, cloned and re-used for each modal.
 */
export class Modal {
	constructor() {
		this.$overlay = $(modalTags.overlay);
		this.$modal = this.$overlay.find(modalTags.body);
		this.$title = this.findTag(modalTags.title);
		this.$closeBtn = this.findTag(modalTags.closeBtn);
		this.$windowTabs = this.findTag(modalTags.tabs);
		this.$modalContent = this.findTag(modalTags.content);
		this.tabContents = [];
		this.tabData = [];
		this._tabIndex = 0;
		this.isAnimating = false;
		this.isOpen = false;
		this.onClose = null;
		this.onKeyDown = this.onKeyDown.bind(this);
	}
	/**
	 * @returns {number}
	 */
	get totalTabs() {
		return this.tabContents.length;
	}

	/**
	 * @param {number} index
	 */
	set tabIndex(index) {
		const total = this.totalTabs;
		this._tabIndex = index === total ? 0 : index;
	}
	get tabIndex() {
		return this._tabIndex;
	}
	findTag(selector) {
		const $tag = this.$modal.find(selector);
		if ($tag.length === 0) {
			throw new Error(`[MODAL_ERROR]: ${selector} was not found in the modal`);
		}
		return $tag;
	}
	changeTitle(title) {
		this.$title.text(title);
	}
	clearModal() {
		this.$windowTabs.empty();
		this.$modalContent.empty();
		this.tabContents = [];
		this.tabIndex = 0;
	}
	/**
	 * renders the modals HTML content; you still must call openModal()
	 * to display it.
	 * @param {string} title
	 * @param {ModalTab[]} modalTabs - must be an array, even for only one item
	 * @returns {void}
	 */
	init(title, modalTabs) {
		if (this.isOpen) {
			throw new Error(
				"Modal is already open and won't be initialized, was this an error in logic?"
			);
		}
		if (modalTabs.length === 0) {
			throw new Error("A Modal must have at least one tab");
		}
		this.changeTitle(title);
		this.tabData = modalTabs;
		modalTabs.forEach((tab) => this.addTab(tab));
		this.addModalEvents();
	}
	/**
	 * @param {ModalTab} tabData
	 */
	addTab(modalTab) {
		if (this.isOpen) {
			throw new Error("Cannot add a tab while the modal is open");
		}
		const { $window, $content } = modalTab;
		this.$windowTabs.append($window);
		this.$modalContent.append($content);
		this.tabContents.push($content);
	}
	/**
	 * @param {Function} onClose - callback for when the modal closes
	 * @returns {void}
	 */
	openModal(onClose = null) {
		if (this.isOpen) {
			console.warn("Modal is already open, was this an error in logic?");
			return;
		}
		if (onClose) {
			this.onClose = onClose;
		}
		modalEvents.fadeInModal(this);
		const firstTab = this.tabData[this.tabIndex];
		if(firstTab.whenVisible) {
			firstTab.whenVisible();
		}
		this.isOpen = true;
	}
	closeModal() {
		if (!this.isOpen) {
			throw new Error(
				"Cannot close the modal, it already closed is this an error?"
			);
		}
		this.$overlay.fadeOut(200, () => {
			$(document).off("keydown", this.onKeyDown);
		});
		this.clearModal();
		this.isOpen = false;
		const currentTab = this.tabData[this.tabIndex];
		console.log("current tab", currentTab);
		console.log("current tab", currentTab);
		if (currentTab.whenHidden) {
			currentTab.whenHidden();
		}
		if (this.onClose) {
			this.onClose();
		}
	}
	/**
	 * @param {number} index
	 * @returns {void}
	 */
	switchTab(index) {
		if (!this.isOpen || this.isAnimating || index === this.tabIndex) {
			return;
		}
		const oldIndex = this.tabIndex;
		this.tabIndex = index;
		this.isAnimating = true;

		const $tabContents = this.$modalContent.find(".tab-content");
		const $windows = this.$windowTabs.find(".tab");
		$windows.eq(oldIndex).removeClass("active").attr("aria-selected", "false");

		$windows.eq(this.tabIndex).addClass("active").attr("aria-selected", "true");
		const $currentTab = $tabContents.eq(oldIndex);
		const $newTab = $tabContents.eq(this.tabIndex);
		this.transitionTabs($currentTab, $newTab, oldIndex);
	}

	transitionTabs($currentTab, $newTab, oldIndex) {
		$currentTab.fadeOut(200, () => {
			const oldTabData = this.tabData[oldIndex];
			if (oldTabData.whenHidden) {
				oldTabData.whenHidden();
			}
			$newTab.fadeIn(200, () => {
				this.isAnimating = false;
				const newTabData = this.tabData[this.tabIndex];
				if (newTabData.whenVisible) {
					newTabData.whenVisible();
				}
			});
		});
	}
	/**
	 * @param {jQuery.Event} event
	 * @returns {void}
	 */
	onKeyDown(event) {
		if (!this.isOpen) {
			return;
		}
		switch (event.key) {
			case "Escape":
				this.closeModal();
				break;
			case "Tab":
				event.preventDefault();
				this.switchTab(this.tabIndex + 1);
				break;
		}
	}
	addModalEvents() {
		this.$closeBtn.on("click", () => {
			if (!this.isOpen) {
				return;
			}
			this.closeModal();
		});

		this.$overlay.on("click", (e) => {
			if (!this.isOpen) {
				return;
			}
			if ($(e.target).is(this.$overlay)) {
				this.closeModal();
			}
		});

		this.$windowTabs
			.on("click", ".tab", (e) => {
				const newTabIndex = $(e.currentTarget).index();
				this.switchTab(newTabIndex);
			})
			.on("keypress", ".tab", (e) => {
				if (!this.isOpen || (e.key !== "Enter" && e.key !== " ")) {
					return;
				}
				e.preventDefault();
				const newTabIndex = $(e.currentTarget).index();
				this.switchTab(newTabIndex);
			});

		this.$modalContent.on("click", ".collapsible-header", (event) => {
			if (!this.isOpen) {
				return;
			}
			event.preventDefault();
			const { type, key } = event;
			if (type === "keypress" && key !== "Enter" && key !== " ") {
				return;
			}
			modalEvents.handleCollapse(event);
		});
	}
}