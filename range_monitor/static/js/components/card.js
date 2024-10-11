// static/js/components/card.js

class Card {
  constructor(description = "") {
    this.desc = description;
    this.data = getCardData();
    this.setup(this.data);
  }
  setup(data) {
    const imageUrl = data.$image.data("image");
    const redirectUrl = data.$button.data("redirect");
    data.$button.on("click", () => {
      window.location.href = redirectUrl;
    });
    data.$image.css("background-image", `url(${imageUrl})`);
    if (this.desc) {
      data.$desc.text(this.desc);
    } else {
      data.$desc.text(
        "Come checkout one of our many resources for the range monitor."
      );
    }
  }
}
// static class used to manage all of the cards
class CardControls {
  /**
   * fade cards in sequentially
   * @param {Card[]} - collection of card instances
   */
  static fadeCardsInOrder(cards) {
    cards.forEach((card, index) => {
      card.$card.css("animation", `fadeIn 0.5s ${index * 0.1}s ease forwards`);
    });
  }
}

function getCardData() {
  const cardsList = [];

  $(".card").each(function () {
    const cardData = {
      $card: $(this),
      $button: $(this).find(".card-btn"),
      $image: $(this).find(".card-image"),
      title: $(this).data("card-name"),
      $desc: $(this).find(".card-desc"),
    };
    cardsList.push(cardData);
  });

  return cardsList;
}
