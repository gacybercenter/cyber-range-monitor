// static/js/components/toggle.js
export { ToggleMessage, ErrorMessage, SuccessMessage };

class ToggleMessage {
  /**
   * @param {string} containerId - the id of the block element to append the message to
   * @param {string} messageType - the css class with the styles you want to apply
   */
  constructor(messageType) {
    this.$container = $(`#toggleMsg`);
    this.messageType = messageType;
    if (this.$container.length === 0) {
      throw new Error(
        `ToggleMessageError: No Container with id '${containerId}' was found`
      );
    }
    this.generate();
  }

  changeMessageType(newMsgType) {
    this.$container.removeClass(this.messageType).addClass(newMsgType);
    this.messageType = newMsgType;
  }

  generate() {
    this.$container.addClass(this.messageType);
    const { $close, $name, $message } = makeTogglerHTML();
    $close.on("click", () => {
      this.hide();
    });

    this.$container.append($close).append($name).append($message);
    this.messageData = { $close, $name, $message };
  }

  hide() {
    if (this.$container) {
      this.$container.fadeOut(500);
    }
  }

  update(message, name, newMsgType = "") {
    this.messageData.$name.text(name);
    this.messageData.$message.text(message);
    if (newMsgType) {
      this.changeMessageType(newMsgType);
    }
  }
  /**
   *
   * @param {string} message - the message to display
   * @param {string} name - the title of the message
   * @param {string} messageType - the new class to apply to the container (e.g success-msg, error-msg)
   */
  show(message, name, messageType = "") {
    this.update(message, name, messageType);
    this.$container.fadeIn(500);
  }
}
/* 
  below are classes that have pre-built css styles that
  are simply applied for ease of use
*/
class ErrorMessage extends ToggleMessage {
  constructor() {
    super("error-msg");
  }
  /**
   * @param {string} message - the message to display
   * @param {string} name - the title of the message
   * @param {string} messageType - the new class to apply to the container (e.g success-msg, error-msg)
   */
  show(message, errorType = "Error: ", newMsgType = "") {
    super.show(message, errorType, newMsgType);
  }
}

class SuccessMessage extends ToggleMessage {
  constructor() {
    super("success-msg");
  }
  /**
   * @param {string} message - the message to display
   * @param {string} name - the title of the message
   * @param {string} messageType - the new class to apply to the container (e.g success-msg, error-msg)
   */
  show(message, successType = "Success:", newMsgType = "") {
    super.show(message, successType, newMsgType);
  }
}

function makeTogglerHTML() {
  const $close = $("<i>", {
    class: "close-btn fas fa-times",
  });
  const $name = $("<strong>", { class: "message-name" });
  const $message = $("<span>", { class: "message-text" });

  return {
    $close,
    $name,
    $message,
  };
}
