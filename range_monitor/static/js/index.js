import { Typer } from "./effects/type_effect.js";

$(document).ready(function () {
  typeHeroText();
});

function typeHeroText() {
  const heroTyper = new Typer("#heroText", 50, 1500);
  const userName = heroTyper.$element.data("username");
  heroTyper.start(
    [
      `Welcome ${userName}, enjoy your stay.`,
      "Big Brother is always watching ",
    ],
    () => {
      $("#heroText").append($("<i></i>").addClass("fas fa-eye iconFade"));
    }
  );
}
