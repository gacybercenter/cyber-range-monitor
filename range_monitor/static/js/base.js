// static/js/base.js

import { StarBackground } from "./effects/star-bg.js";
import { animateAlerts } from "./components/alerts.js";

$(document).ready(function () {
  StarBackground.initalize();
  animateAlerts();
});
