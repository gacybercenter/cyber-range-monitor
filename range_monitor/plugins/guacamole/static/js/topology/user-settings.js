import { Modal } from "./user-interface/node-modal.js/guac-modal.js";
import { settingsModalData } from "./user-interface/node-modal.js/settings-modal.js";



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

export function initSettingsModal(topology) {
	const { updateScheduler, context, userSettings } = topology;
	const toggleBtn = ($btn, flag) => {
		const icon = $btn.find("i");
		icon.fadeOut(200, function () {
			if (flag) {
				icon.removeClass("fa-times").addClass("fa-check");
			} else {
				icon.removeClass("fa-check").addClass("fa-times");
			}
			icon.fadeIn(200);
		});
		$btn.toggleClass("active");
	};

	const settingBtnEvents = () => {
		console.log(`refreshEnabled => ${userSettings.refreshEnabled}`);
		$("#toggle-enable-refresh").on("click", function () {
			topology.toggleRefresh();
			toggleBtn($(this), userSettings.refreshEnabled);
			const $speedContainer = $(".refresh-speed");
			if (userSettings.refreshEnabled) {
				$speedContainer.slideDown(300);
			} else {
				$speedContainer.slideUp(300);
			}
		});
		$("#toggle-show-inactive").on("click", function () {
			topology.toggleInactive();
			toggleBtn($(this), userSettings.showInactive);
		});
	};


	const updateRefreshStatus = () => {
		if(userSettings.refreshEnabled) {
			$("#refresh-countdown")
					.text(new Date(updateScheduler.lastUpdated + updateScheduler.delay)
					.toLocaleTimeString());			
		} else {
			$("#refresh-countdown").text("Disabled");
		}
	};

	$("#menuToggler").on("click", function () {
		const modalData = settingsModalData(context, updateScheduler, userSettings);
		const settingsModal = new Modal();
		settingsModal.init("Topology Settings", modalData);
		settingBtnEvents();
		if(!userSettings.refreshEnabled) {
			$(".refresh-speed").hide();
		}
		speedOptionEvents(updateScheduler, userSettings.refreshEnabled);
		const uptimeId = setUptimeCounter(updateScheduler.upTime);
		const refreshId = setInterval(() => {
			updateRefreshStatus()
		}, updateScheduler.delay - 5000);
		settingsModal.openModal(function () {
			clearInterval(uptimeId);
			if(refreshId) {
				clearInterval(refreshId);
			}
		});
	});
}

const speedOptionEvents = (updateScheduler, refreshEnabled) => {
	$(`.speed-option[data-speed="${updateScheduler.stringDelay}"]`)
		.addClass("selected");
	$(".speed-option").on("click", function () {	
		if ($(this).hasClass("selected") || !refreshEnabled) {
			return;
		}
		const $speedOptions = $(".speed-option");
		$speedOptions.removeClass("selected");
		$speedOptions
			.find("i.fa-check-square")
			.fadeOut(200, function () {
				$(this)
					.removeClass("fas fa-check-square")
					.addClass("far fa-square")
					.fadeIn(200);
			});
		$(this).addClass("selected");
		$(this)
			.find("i.fa-square")
			.fadeOut(200, function() { 
				$(this)
					.removeClass("far fa-square")
					.addClass("fas fa-check-square")
					.fadeIn(200);
			});			
		const rate = $(this).attr("data-speed");
		updateScheduler.setDelay(rate);
	});
};

function setUptimeCounter(startTime) {
	const uptimeId = setInterval(() => {
		const pad = (num) => {
			return (num < 10)? `0` + num : num;
		};
		
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
		const hours = Math.floor(elapsed / 3600);
		const minutes = Math.floor((elapsed % 3600) / 60);
		const seconds = elapsed % 60;

		$("#uptime-field").text(`${pad(hours)}:${pad(minutes)}:${pad(seconds)}`);	
	}, 1000);
	return uptimeId;
}