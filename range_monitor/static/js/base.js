// static/js/base.js

import { StarController  } from './effects/star-bg.js';
import { initAlerts } from './components/alerts.js';
import { TypingAnimation } from "./effects/typing-animation.js";

$(function () {
    const starController = new StarController();
    
    initAlerts();

    const $curPage = $("#curPage");
    const typeCurrentPage = new TypingAnimation($curPage, 50, 300);
    typeCurrentPage.typeMessage($curPage.text());
});


