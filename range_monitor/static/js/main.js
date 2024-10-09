// static/js/main.js

import { starBackground  } from './components/dynamic-bg.js';
import { initAlerts } from './components/alerts.js';



$(function () {
    // initialize the star background
    const bgManager = starBackground();
    bgManager.initalize();
    
    // init the alert bar effects
    initAlerts();

});


