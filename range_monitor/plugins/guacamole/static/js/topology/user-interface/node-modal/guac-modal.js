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

export class Modal {
	constructor() {
		this.$overlay = $(modalTags.overlay);
		this.$modal = this.$overlay.find(modalTags.body);
		this.$title = this.findTag(modalTags.title);
		this.$closeBtn = this.findTag(modalTags.closeBtn);
		this.$windowTabs = this.findTag(modalTags.tabs);
		this.$modalContent = this.findTag(modalTags.content);
		this.tabContents = [];
		this._tabIndex = 0;
		this.isAnimating = false;
		this.isOpen = false;
		this.onClose = null;
		this.onKeyDown = this.onKeyDown.bind(this);
		this.addModalEvents();
	}

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

	/**
	 * @param {string} selector
	 * @returns {JQuery<HTMLElement>} - the tag found
	 */
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
	 * renders the modals HTML content and empties the contents
	 * of a possible previous modal. you still must call openModal()
	 * to display it.
	 * @param {string} title
	 * @param {ModalTab[]} modalTabs - must be an array, even for only one item
	 * @returns {void}
	 */
	init(title, modalTabs) {
		if (this.isOpen) {
			console.warn(
				"Modal is already open and won't be initialized, was this an error in logic?"
			);
			return;
		}
		if (modalTabs.length === 0) {
			throw new Error("Modal must have at least one tab");
		}
		this.clearModal();
		this.changeTitle(title);
		modalTabs.forEach((tab) => this.addTab(tab));
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
		modalEventHandlers.fadeInModal(this);
		this.isOpen = true;
	}

	switchTab(index) {
		if (!this.isOpen || this.isAnimating || index === this.tabIndex) {
			return;
		}

		const oldIndex = this.tabIndex;
		this.tabIndex = index;

		this.isAnimating = true;

		const $tabContents = this.$modalContent.find(".tab-content");

		const $oldTab = $tabContents.eq(oldIndex);
		const $newTab = $tabContents.eq(this.tabIndex);

		const $windows = this.$windowTabs.find(".tab");
		$windows
			.eq(oldIndex)
			.removeClass("active")
			.attr("aria-selected", "false");

		$windows
			.eq(this.tabIndex)
			.addClass("active")
			.attr("aria-selected", "true");

		$oldTab.fadeOut(200, () => {
			$newTab.fadeIn(200, () => {
				this.isAnimating = false;
				this.tabIndex = index;
				const newTabData = this.tabContents[this.tabIndex];
				if (newTabData.whenVisible) {
					newTabData.whenVisible();
				}
			})
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
				modalEventHandlers.closeModal(this);
				break;
			case "Tab":
				event.preventDefault();
				this.switchTab(this.tabIndex + 1);
				break;
		}
	}

	addModalEvents() {
		// ensures modal events trigger only when modal is opened
		const guardEvent = (callback) => {
			return (...args) => {
				if (!this.isOpen) {
					return;
				}
				return callback(...args);
			};
		};

		const changeTabIndex = (e) => {
			const newTabIndex = $(e.currentTarget).index();
			console.log("new tab index", newTabIndex);
			this.switchTab(newTabIndex);
		};

		this.$closeBtn.on(
			"click",
			guardEvent(() => modalEventHandlers.closeModal(this))
		);

		this.$overlay.on(
			"click",
			guardEvent((event) => {
				if ($(event.target).is(this.$overlay)) {
					modalEventHandlers.closeModal(this);
				}
			})
		);

		this.$windowTabs
			.on(
				"click",
				".tab",
				guardEvent((event) => changeTabIndex(event))
			)
			.on(
				"keypress",
				".tab",
				guardEvent((event) => {
					if (event.key !== "Enter" && event.key !== " ") {
						return;
					}
					event.preventDefault();
					changeTabIndex(event);
				})
			);

		this.$modalContent.on(
			"click keypress",
			".collapsible-header",
			guardEvent((event) => {
				const { type, key } = event;
				if (type === "keypress" && key !== "Enter" && key !== " ") {
					return;
				}
				event.preventDefault();
				modalEventHandlers.handleCollapse(event);
			})
		);
	}
}

const modalEventHandlers = {
	/**
	 * @summary
	 * handles collapsing a collapsible
	 * when it's clicked
	 * @param {jQuery.Event} event
	 */
	handleCollapse(event) {
		const $header = $(event.currentTarget);
		const $content = $header.next(".collapsible-content");
		
		const $toggleIcons = $header.find(".collapse-toggle");

		const isExpanded = ($header.attr("aria-expanded") === "true");
		$header.attr("aria-expanded", !isExpanded);
		
		$content.toggleClass("expanded");
		$toggleIcons.toggleClass("active");
	},
	/**
	 * fades in the modal when it is opened
	 * @param {Modal} modal
	 */
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
			console.log("window", $windowTabs.find(".tab").eq(0).length);

			activateFirst($windowTabs, ".tab").focus();
			activateFirst($modalContent, ".tab-content").show();

			$(document).on("keydown", modal.onKeyDown);
		});
	},
	/**
	 * @param {Modal} modal
	 */
	closeModal(modal) {
		if (!modal.isOpen) {
			console.warn(
				"Cannot close the modal, it already closed is this an error?"
			);
		}
		modal.$overlay.fadeOut(200, () => {
			$(document).off("keydown", modal.onKeyDown);
		});
		modal.isOpen = false;
		if (modal.onClose) {
			modal.onClose();
		}
	},
};

