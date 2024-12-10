import { Modal } from "../user-interface/node-modal/guac-modal.js";
import { createSettingsModal } from "../user-interface/node-modal/settings-modal.js";


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
	initSettingsModal(topology) {
		$("#menuToggler").on("click", () => {
			const settingsTabs = createSettingsModal(topology);
			const settingsModal = new Modal();
			settingsModal.init("Settings", settingsTabs);
			settingsModal.openModal();
		});
	}
}
