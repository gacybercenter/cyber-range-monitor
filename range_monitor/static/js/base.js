// static/js/base.js

import { StarBackground  } from './effects/star-bg.js';
import { initAlertBar } from "./components/alerts.js";
import { Typer } from "./effects/typer.js";

$(function () {
    StarBackground.initalize(); // initalize background effect
    initAlertBar(); // create alert bar 

    // type the current page title
    const typePage = new Typer($("#pageTitle"), 50, 300);
    typePage.typeMessage($("#pageTitle").text());



});



