// static/js/components/star-bg.js

// change config as needed
const effectConfig = {
  starCount: 150,
  starColor: "white",
  minSize: 1,
  maxSize: 3,
  animationDuration: 20, // secs
};

export class StarBackground {
  /**
   * Creates a star background effect
   * and instance to manage all tags with the effect.
   * Can be disabled or enabled with class methods
   */
  static initalize() {
    $(".add-stars").each(function () {
      initStar($(this));
    });
  }

  /**
   * Disables the star background effect
   * on all tags
   */
  static disable() {
    $(".add-stars").each(function () {
      removeStars($(this));
    });
  }
  /**
   * removes the effect on a specified tag useful
   * for removing the effect on a single tag thats
   * in the base html template
   * @param {*} tagIdentifier (tag name, class, or id)
   */
  static removeStarsFrom(tagIdentifier) {
    $(tagIdentifier).each(function () {
      removeStars($(this));
    });
  }
  /**
   * adds the effect on a specified tag useful
   * for adding the effect on a single tag thats
   * doesnt have the add-star class in the base html
   * template
   * @param {*} tagIdentifier (tag name, class, or id)
   */
  static addStarsTo(tagIdentifier) {
    $(tagIdentifier).each(function () {
      $(this).addClass("add-stars");
    });
    StarBackground.initalize();
  }
}
// utils
function removeStars($tag) {
  $tag.removeClass("add-stars");
  $tag.find(".star-container").remove();
}
function createStar($container) {
  const size =
    Math.random() * (effectConfig.maxSize - effectConfig.minSize) +
    effectConfig.minSize;
  const $star = $("<div></div>").addClass("star");
  $star.css({
    width: `${size}px`,
    height: `${size}px`,
    top: `${Math.random() * 100}%`,
    left: `${Math.random() * 100}%`,
    animation: `twinkle 
		  	${Math.random() * effectConfig.animationDuration + 5}s 
		  infinite, 
		  float 
		  	${Math.random() * (effectConfig.animationDuration - 10) + 10}s 
		  linear infinite`,
  });
  $container.append($star);
}
function initStar($tag) {
  if ($tag.css("position") === "static") {
    $tag.css("position", "relative");
  }
  const $starContainer = $("<div></div>").addClass("star-container");

  for (let i = 0; i < effectConfig.starCount; i++) {
    createStar($starContainer);
  }
  $tag.append($starContainer);
}
