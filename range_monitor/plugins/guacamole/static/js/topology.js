// static/js/topology.js
import { Topology } from "./topology/main_ui.js";

import {
	NavigationHints 
} from "./topology/user-interface/ui_hints.js";



$(function () {
	const topology = new Topology();
	NavigationHints.init();
	topology.statusUI.loading();
	topology.render(true);
});
