import { Cards } from "./components/card.js";

$(document).ready(function () {
  $(".card").each(function () {
    const id = $(this).attr("id");
    $(this)
      .find(".card-btn")
      .data("redirect", "/sources/" + id);
  });
  const cards = Cards.createAll();
});
