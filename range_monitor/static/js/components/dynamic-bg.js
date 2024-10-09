// static/js/components/dynamic-bg.js

// change config as needed
const starBackgroundConfig = {
	starCount: 150,
	starColor: "white",
	minSize: 1,
	maxSize: 3,
	animationDuration: 20, // secs
};
const createStar = ($container) => {
	const size =
		Math.random() *
		(starBackgroundConfig.maxSize - starBackgroundConfig.minSize) +
		starBackgroundConfig.minSize;
	const $star = $("<div></div>").addClass("star");
	$star.css({
		width: `${size}px`,
		height: `${size}px`,
		top: `${Math.random() * 100}%`,
		left: `${Math.random() * 100}%`,
		animation: 
		  `twinkle 
		  	${Math.random() * starBackgroundConfig.animationDuration + 5}s 
		  infinite, 
		  float 
		  	${Math.random() * (starBackgroundConfig.animationDuration - 10) + 10}s 
		  linear infinite`,
	});
	$container.append($star);
};
const initalizeStars = () => {
	$(".add-stars").each(function () {
		if ($(this).css("position") === "static") {
			$(this).css("position", "relative");
		}
		const $starContainer = $("<div></div>").addClass("star-container");
		
		for (let i = 0; i < starBackgroundConfig.starCount; i++) {
			createStar($starContainer);
		}
		$(this).append($starContainer);
	});
};
const deleteStar = ($star) => {
	$star.removeClass("add-stars");
	$star.find(".star-container").remove();
}
const removeStarsFrom = (tagIdentifier) => {
	$(tagIdentifier).each(function () {
		deleteStar($(this));
	});
};
const addStarsTo = (tagIdentifier) => {
	$(tagIdentifier).each(function () {
		$(this).addClass("add-stars");
	});
};
const disableStars = () => {
	$(".add-stars").each(function () {
		deleteStar($(this));
	});
};
/**
 * Returns an object with methods for manipulating 
 * & initalizing the star background effect
 * @returns {Object} - object used to control the star background
*/
export const starBackground = () => {
	return {
		/**
		 * Must be called for the star background to
		 * be rendered. Renders the star backgrounds 
		 * on all elements with the "add-stars" class. 
		*/
		initialize: initalizeStars,
		/**
		 * Adds the"add-stars" class to the specified tag
		 * NOTE you still need to call initialize() to see the stars
		 * and should call this before initialize()
		 * @param {string} tagIdentifier - (i.e, tag, class, id)
		 * to look for
		*/
		addStarsTo: addStarsTo,
		/**
		 * Removes "add-stars" class from the specified tag
		 * identifier
		 * @param {string} tagIdentifier - (i.e, tag, class, id)
		*/
		removeStarsFrom: removeStarsFrom,
		/**
		 * Completely disables the star background by
		 * deleting the "add-stars" class and the "star-container"
		 * element completely
		*/
		disable: disableStars,
	};
};
