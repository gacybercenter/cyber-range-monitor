import { Typer } from "./effects/type_effect.js";
import { Cards } from "./components/card.js";

$(document).ready(function () {
  typeHeroText();
  const cards = Cards.createAll();
  // ^- this will initalize and return
  // the object to manipulate the cards
});

function typeHeroText() {
  const heroTyper = new Typer("#heroText", 50, 1000);
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
