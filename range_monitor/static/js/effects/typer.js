// static/js/components/typer.js

// re-usable typing animation class
export class Typer {
  /**
   * Creates a typing animation given at least a jQuery element
   * typingSpeed and delay are optional
   * @param {String} elementId - id of the element to type to
   * @param {Number} typingSpeed in miliseconds  (default=150)
   * @param {Number} delay  in miliseconds (default=1000)
   * throws TyperAnimationError if the element is not found
   */
  constructor(elementId, typingSpeed = 150, delay = 1000) {
    this.$element = $(elementId);
    this.typingSpeed = typingSpeed;
    this.delay = delay;
    checkTypingAnimation(this, elementId);
    this.$element.addClass("typed-text");
  }
  /**
   * Types a single message to the corresponding
   * element when it is visible in the viewport
   * @param {*} text
   */
  typeMessage(text) {
    animateWhenVisible(this.$element[0], () => {
      tryToType(this, text).catch((error) => {
        console.error(`TyperError: ${varDebugInfo("text", text)}`, error);
      });
    });
  }
  /**
   * Types a "group" (i.e array) of messages to the corresponding
   * element when it is visible in the viewport
   * @param {string[]} messages - list of messages to type
   * @param {Number} messageDelay - the pause between each message (default=5000)
   */
  typeMessages(messages, messageDelay = 5000) {
    messages.forEach((message, index) => {
      setTimeout(() => this.typeMessage(message), index * messageDelay);
    });
  }
  /**
   * Given a group of messages and a delay it returns
   * the total time it will take to type all the messages
   * useful for setting timeouts and guaging your typing speed
   * & delay properties
   * @param {string[]} messages
   * @param {Number} messageDelay
   * @returns
   */
  calculateDuration(messages, messageDelay) {
    return (
      (messages.length - 1) * messageDelay +
      messages.reduce((sum, msg) => sum + msg.length * this.typingSpeed, 0) +
      this.delay
    );
  }
}
class TyperAnimationError extends Error {
  constructor(message) {
    super(message);
    this.name = "TyperAnimationError";
  }
}
function validateTyper(typer, tagId) {
  const validNum = (num) => typeof num === "number" && num > 0;
  if (!typer.$element.length) {
    return [false, `The element with the "${tagId}" ID was not found.`];
  }
  if (!validNum(typer.typingSpeed) || !validNum(typer.delay)) {
    const errorInfo =
      varDebugInfo("typingSpeed", typer.typingSpeed) +
      ", " +
      varDebugInfo("delay", typer.delay);
    return [
      false,
      `The typing speed and delay must be positive numbers.\n${errorInfo}`,
    ];
  }
  return [true, null];
}
// useful sanity check because of ambigous typing
function varDebugInfo(varName, varValue) {
  return `${varName}=[${varValue},type=${typeof varValue}]`;
}
function checkTypingAnimation(typer, tagId) {
  const [isValid, error] = validateTyper(typer, tagId);
  if (!isValid) {
    throw new TyperAnimationError(error);
  }
}
/**
 * using the IntersectionObserver API and callback
 * animations can be trigger when an element is in
 * the viewport
 * NOTE (may move to a utility file later)
 * @param {HTMLElement} element - not a jQuery one; use .get(0) to convert it
 * @param {Function} callback - the animation to trigger
 **/
function animateWhenVisible(element, callback) {
  const watcher = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        try {
          callback();
          observer.unobserve(entry.target);
        } catch (error) {
          console.error("Error in animateWhenVisible callback:", error);
        }
      }
    });
  });
  watcher.observe(element);
}
function tryToType(typer, text) {
  return new Promise((resolve, reject) => {
    if (!typer.$element) {
      reject(new Error("Element not found"));
      return;
    }
    typer.$element.empty();
    let i = 0;
    const type = () => {
      if (i < text.length) {
        typer.$element.text((_, oldText) => oldText + text.charAt(i));
        i++;
        setTimeout(type, typer.typingSpeed);
      } else {
        resolve();
      }
    };
    setTimeout(type, typer.delay);
  });
}
