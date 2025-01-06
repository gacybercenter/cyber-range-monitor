// static/js/effects/type_effect.js
class Typer {
  /**
   * Creates a Typing Animation
   * @param {string} elementId - the id of the element to type in
   * @param {Number} speed (default=100 )
   * @param {Number} delay (default=1000 )
   */
  constructor(elementId, speed = 100, delay = 1000) {
    this.$element = $(elementId);
    this.speed = speed;
    this.delay = delay;
    this.cursorChar = '<span class="blinking-cursor">|</span>';
    this.$element.addClass("typer-config");
  }

  /**
   * start the typing animation
   * @param {string[]} messages - the messages to type; if a single just wrap in square brackets
   * @param {function} callback - the action to perform after typing
   */
  start(messages, callback = null) {
    this.messages = messages;
    if(this.$element.length === 0){
      console.log("Element not found and could not perform animation");
      return;
    }
    typeMessages(this, () => {
      this.$element.html(this.$element.html().replace(this.cursorChar, ""));
      console.log("ok");
      if (callback) {
        callback();
      }
    });
  }
}
function typeMessage(typer, text, callback) {
  let index = 0;
  function typeChar() {
    if (index < text.length) {
      typer.$element.html(text.substring(0, index + 1) + typer.cursorChar);
      index++;
      setTimeout(typeChar, typer.speed);
    } else if (callback) {
      callback();
    }
  }

  typeChar();
}

function typeMessages(typer, callback) {
  let index = 0;
  function nextMessage() {
    if (index < typer.messages.length) {
      typer.$element.html("");
      typeMessage(typer, typer.messages[index], () => {
        index++;
        setTimeout(nextMessage, typer.delay);
      });
    } else if (callback) {
      callback();
    }
  }
  nextMessage();
}


export { Typer };
