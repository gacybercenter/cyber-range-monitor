// static/js/topology.js
import { topology } from "./topology/main_ui.js";

import {
	NavigationHints 
} from "./topology/user-interface/ui_hints.js";

$(function () {
	NavigationHints.init();
	topology.loadScreen.loading();
	topology.render(true);
});
