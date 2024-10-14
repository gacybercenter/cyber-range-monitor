// static/js/components/toggle.js
export { ToggleMessage, ErrorMessage, SuccessMessage };

class ToggleMessage {
  /**
   * @param {string} messageType - the css class with the styles you want to apply
   */
  constructor(messageType) {
    this.$container = $(`#toggleMsg`);
    this.messageStyle = messageType;
    if (this.$container.length === 0) {
      throw new Error(
        `ToggleMessageError: No Container with id '${containerId}' was found`
      );
    }
    this.generate();
  }

  changeMessageStyle(newMsgType) {
    this.$container.removeClass(this.messageStyle).addClass(newMsgType);
    this.messageStyle = newMsgType;
  }

  generate() {
    this.$container.addClass(this.messageStyle);
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
      this.changeMessageStyle(newMsgType);
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
