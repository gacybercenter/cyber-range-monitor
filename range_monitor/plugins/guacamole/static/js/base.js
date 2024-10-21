import { NetworkSimulation } from "./effects/nw-canvas/nw-simulation.js";



$(document).ready(() => {
    const $container = NetworkSimulation.findContainer();
    const simulation = new NetworkSimulation($container);
    simulation.run();
});

