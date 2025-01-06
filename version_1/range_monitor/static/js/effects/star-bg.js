// static/js/components/star-bg.js

// change config as needed
export const effectConfig = {
  starCount: 150,
  starColor: "white",
  minSize: 1,
  maxSize: 3,
  animationDuration: 20, // secs
};

export class StarBackground {
  /**
   * loads the starbackground effect
   */
  static initalize() {
    const [hasTags, $stars] = fetchStarTags();
    
    if (!hasTags) return;

    $stars.each(function () {
      initStar($(this));
    });
  }

  /**
   * Disables effect on all tags
   */
  static disable() {
    const [hasTags, $stars] = fetchStarTags();
    
    if (!hasTags) return; 

    $stars.each(function () {
      removeStars($(this));
    });
  }

  /**
   * removes the effect on a specified tag
   * @param {string} tagIdentifier (tag name, class, or id)
   */
  static removeStarsFrom(tagIdentifier) {
    const $tags = $(tagIdentifier);
    if ($tags.length === 0) {
      console.log(`StarBackground: No tags with identifier ${tagIdentifier} were found`);
      return;
    }
    $tags.each(function () {
      removeStars($(this));
    });
  }
  /**
   * adds the effect on a specified tag
   * @param {string} tagIdentifier (tag name, class, or id)
   */
  static addStarsTo(tagIdentifier) {
    const $tags = $(tagIdentifier);
    if ($tags.length === 0) {
      console.log(`StarBackground: No tags with identifier ${tagIdentifier} were found`);
      return;
    }
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
function fetchStarTags() {
  const $stars = $(".add-stars");
  if ($stars.length === 0) {
    console.log("No tags with the add-stars class found");
    return [false, null];
  }
  return [true, $stars];
}

