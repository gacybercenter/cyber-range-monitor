import { Modal } from "../user-interface/node-modal/guac-modal.js";
import { settingsModalData } from "../user-interface/node-modal/settings-modal.js";


export class UserSettings {
  constructor() {
    this.refreshEnabled = true;
    this.showInactive = true;
    this.labelPreferences = {
      hideAll: false,
      hideInactive: false,
      hideGroups: false,
    };
    this.iconPreferences = {
      hideAll: false,
      useOS: false,
      useConnectionCount: false
    };
  }
}

export const settingsUI = {
	/**
	 * 
	 * @param {UserSettings} userSettings 
	 * @param {topology} topology 
	 */
	bindEvents(userSettings, topology) {
		console.log("toggle refresh: ", $("#toggle-enable-refresh").length);
		$("#toggle-enable-refresh").click(function () {
			topology.toggleRefresh();
			settingEvents.btnToggler($(this), userSettings.refreshEnabled);
			if (userSettings.refreshEnabled) {
				$(".refresh-speed").slideDown(300);
				return;
			} 
			$(".refresh-speed").slideUp(300);
		});
		$("#toggle-show-inactive").click(function() {
			topology.toggleInactive();
			settingEvents.btnToggler($(this), userSettings.showInactive);
		});
	},
	/**
	 * creates and initializes the settings modal
	 * @param {topology} topology 
	 */
	initialize(topology) {
		$("#menuToggler").click(() => {
			const { updateScheduler, context, userSettings } = topology;
			const modalTabData = settingsModalData(
				context, updateScheduler, userSettings
			);
			const settingsModal = new Modal();
			settingsModal.init("Topology Settings", modalTabData);
			this.bindEvents(userSettings, topology);
			if(!userSettings.refreshEnabled) {
				$(".refresh-speed").hide();
			}
			$(`.speed-option[data-speed="${updateScheduler.stringDelay}"]`)
				.addClass("selected");
			settingEvents.speedOptionEvents(updateScheduler, userSettings);
			let { uptimeId, refreshId } = settingEvents.uiIntervals(
				updateScheduler, userSettings
			);
			settingsModal.openModal(() => {
				clearInterval(uptimeId);
				clearInterval(refreshId);
				refreshId = null;
				uptimeId = null;
			});
		});
	},
};

const settingEvents = {
	/**
	 * @param {JQuery<HTMLElement>} $btn 
	 * @param {boolean} flag 
	 */
	btnToggler($btn, flag) {
		const icon = $btn.find("i");		
		let remove = "fa-check", add = "fa-times";
		if(flag) {
			remove = "fa-times", add = "fa-check";
		} 
		icon.fadeOut(200, function () {
			icon
				.removeClass(remove)
				.addClass(add)
				.fadeIn(200);
		});
		$btn.toggleClass("active");
	},
	/**
	 * @param {updateScheduler} updateScheduler 
	 * @param {UserSettings} userSettings 
	 */
	updateNextRefresh(updateScheduler, { refreshEnabled }) {
		const { scheduler, delay } = updateScheduler;
		if(refreshEnabled && scheduler?.lastExecuted) {
			const nextRefresh = new Date(scheduler.lastExecuted + delay);
			$("#refresh-countdown").text(nextRefresh.toLocaleTimeString());			
		} else {
			$("#refresh-countdown").text("Disabled");
		}
	},
	/**
	 * @param {*} startTime 
	 * @returns {Number}
	 */
	setUptimeCounter(startTime) {
		const pad = (num) => {
			return (num < 10)? `0` + num : num;
		};
		const uptimeId = setInterval(() => {
  	  const elapsed = Math.floor((Date.now() - startTime) / 1000);
			const hours = Math.floor(elapsed / 3600);
			const minutes = Math.floor((elapsed % 3600) / 60);
			const seconds = elapsed % 60;
			$("#uptime-field").text(`${pad(hours)}:${pad(minutes)}:${pad(seconds)}`);	
		}, 1000);
		return uptimeId;
	},
	/**
	 * @param {updateScheduler} updateScheduler 
	 * @param {UserSettings} userSettings 
	 */
	speedOptionEvents(updateScheduler, { refreshEnabled }) {
		// NOTE ^- maybe move this 
		$(".speed-option").click(function() {	
			if ($(this).hasClass("selected") || !refreshEnabled) {
				return;
			}
			const $speedOptions = $(".speed-option");
			$speedOptions.removeClass("selected");
			settingEvents.toggleCheckbox($speedOptions.find("i.fa-check-square"), false);

			$(this).addClass("selected");
			settingEvents.toggleCheckbox($(this).find("i.fa-square"), true);
			
			const rate = $(this).attr("data-speed");
			updateScheduler.setDelay(rate);
		});
	},
	/**
	 * @param {updateScheduler} updateScheduler 
	 * @param {UserSettings} userSettings 
	 * @returns {Object}
	 */
	uiIntervals(updateScheduler, userSettings) {
		const uptimeId = this.setUptimeCounter(updateScheduler.upTime);
		// Update interval checking more frequently to ensure UI stays in sync
		const refreshId = setInterval(() => {
			this.updateNextRefresh(updateScheduler, userSettings);
		}, 1000); // Check every second instead of waiting for full delay
		return { uptimeId, refreshId };
	},
	toggleCheckbox($icon, toggleOn) {
		let remove, add;
		if(toggleOn) {
			remove = "far fa-square";
			add = "fas fa-check-square";
		} else {
			remove = "fas fa-check-square";
			add = "far fa-square";
		}
		$icon.fadeOut(200, function() {
			$(this)
				.removeClass(remove)
				.addClass(add)
				.fadeIn(200);
		});
	}
};