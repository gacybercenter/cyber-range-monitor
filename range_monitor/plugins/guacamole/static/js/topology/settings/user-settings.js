import { Modal } from "../user-interface/node-modal/guac-modal.js";
import { createSettingsModal } from "../user-interface/node-modal/settings-modal.js";


export const userSettings = {
	refreshEnabled: true,
	showInactive: true,
	labelPreference: "show-all",
	iconPreference: "use-os",
	allowedRetries: "some",
	refreshSpeed: "medium",
	initSettingsModal(topology) {
		$("#menuToggler").on("click", () => {
			const settingsTabs = createSettingsModal(topology);
			const settingsModal = new Modal();
			settingsModal.init("Settings", settingsTabs);
			settingsModal.openModal();
		});
	},
	canChangeLabel(preference) {
		if(preference === userSettings.labelPreference) {
			return false;
		}
		if(!userSettings.showInactive && preference === "hide-inactive") {
			return false;
		}
		return true;
	}
};




class SubPreference {
  constructor(status, dataValue) {
    this.status = status;
    this.dataValue = dataValue;
  }
}




