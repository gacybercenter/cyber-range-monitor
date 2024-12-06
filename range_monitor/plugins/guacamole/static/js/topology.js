// static/js/topology.js
import { topology } from "./topology/render.js";

import {
	NavigationHints 
} from "./topology/user-interface/misc/ui_hints.js";

$(function () {
	NavigationHints.init();
	topology.loadScreen.loading();
	topology.render(true);
});