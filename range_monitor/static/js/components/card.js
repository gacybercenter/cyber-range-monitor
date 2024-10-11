// static/js/components/card.js
export class Cards {
  static create($tag, desc = "") {
    const card = {
      $tag,
      id: $tag.attr("id"),
      $desc: $tag.find(".card-desc"),
    };
    const description = desc || defaultDescription(card.id);
    card.$desc.text(description);
    setCardDisplay($tag);
    return card;
  }

  static createAll() {
    const cardsList = [];
    $(".card").each(function (index) {
      let delay = (index + 1) * 0.1;
      $(this)
        .delay(delay * 1000)
        .fadeIn(1000);
      cardsList.push(Cards.create($(this)));
    });
    return cardsList;
  }
  static addDescriptionTo(desc, cardId) {
    $(`#${cardId} .card-desc`).text(desc);
  }
}
// utils
function defaultDescription(id) {
  return `Checkout ${id} one of our many resources for the range monitor.`;
}

function setCardDisplay($tag) {
  const $img = $tag.find(".card-image");
  const $btn = $tag.find(".card-btn");

  const imageUrl = $img.data("image");
  const redirectUrl = $btn.data("redirect");
  const goToRedirect = () => {
    window.location.href = redirectUrl;
  };
  $tag.on("click", goToRedirect);
  $btn.on("click", goToRedirect);
  $img.css("background-image", `url(${imageUrl})`);
}
