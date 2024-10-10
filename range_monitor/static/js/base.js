// static/js/base.js

import { StarBackground } from "./effects/star-bg.js";
import { initAlertBar } from "./components/alerts.js";
import { Typer } from "./effects/type_effect.js";

$(document).ready(function () {
  StarBackground.initalize(); // initalize background effect
  initAlertBar(); // create alert bar

  const currentPage = $("#pageTitle").text() ?? "Home";

  const typer = new Typer("#pageTitle", 200, 1500);
  typer.start([currentPage]);
});
