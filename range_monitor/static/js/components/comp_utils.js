// static/js/components/comp_utils.js
class AnimationPropertyError extends Error {
  constructor(propertyName, message) {
    super(`Invalid ${propertyName}: ${message}`);
    this.name = "AnimationPropertyError";
  }
}

/**
 * represents a set of CSS animation properties.
 */
class AnimationOptions {
  /**
   * Creates an instance of AnimationOptions.
   * @param {Object} params - Parameters including all animation properties.
   */
  constructor(params) {
    this.properties = {
      name: params.name,
      duration: this.validateTime(params.duration, "duration"),
      timingFunction: params.timingFunction || "ease",
      delay: this.validateTime(params.delay, "delay"),
      iterationCount: this.validateIterationCount(params.iterationCount),
      direction: params.direction || "normal",
      fillMode: params.fillMode || "none",
      playState: params.playState || "running",
    };
  }

  validateTime(timeStr, propertyName) {
    if (!/^[0-9]+(s|ms)$/.test(timeStr)) {
      throw new AnimationPropertyError(
        propertyName,
        `${timeStr}. Must be a string ending in 's' or 'ms'.`
      );
    }
    return timeStr;
  }

  validateIterationCount(count) {
    if (typeof count !== "number" && count !== "infinite") {
      throw new AnimationPropertyError(
        "iteration-count",
        `Must be a number or "infinite", got ${typeof count}.`
      );
    }
    return count;
  }
}

/**
 * sets CSS animation properties on a specified jQuery element using an AnimationOptions object.
 * @param {jQuery} $element - jQuery element to which the animation will be applied.
 * @param {AnimationOptions} options - an instance of AnimationOptions containing animation settings.
 */
function setAnimationProperties($element, options) {
  $element.css(options.properties);
}

// example usage?
// $(document).ready(() => {
//   try {
//     const animOptions = new AnimationOptions({
//       name: "fadeIn",
//       duration: "2s",
//       timingFunction: "ease-in-out",
//       delay: "1s",
//       iterationCount: "infinite",
//       direction: "alternate",
//       fillMode: "forwards",
//       playState: "running",
//     });
//     setAnimationProperties($("#element"), animOptions);
//   } catch (error) {
//     console.error(error.message);
//   }
// });
