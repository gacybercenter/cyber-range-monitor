// static/js/components/toggle.js

function makeTogglerHTML() {
  const $closeBtn = $("<i>", { class: "close-btn fas fa-times" });
  const $name = $("<strong>", { class: "toggle-message-name" });
  const $message = $("<span>", { class: "toggle-message-text" });

  return {
    $closeBtn,
    $name,
    $message,
  };
}
export class ToggleMessage {
  /**
   * @param {string} cssClass - the css class with the styles you want to apply
   */
  constructor(cssClass) {
    this.$container = $(`#toggleMsg`);
    this.cssClass = cssClass;
    this.msgData = {};

    if (this.$container.length === 0) {
      throw new Error(
        `ToggleMessageError: No Container with id '${containerId}' was found`
      );
    }
    this.initalize();
  }
  initalize() {
    this.$container.addClass(this.cssClass);
    this.msgData = makeTogglerHTML();

    this.msgData.$closeBtn.click(() => {
      this.hide();
    });

    this.$container.append(
      this.msgData.$closeBtn, 
      this.msgData.$name, 
      this.msgData.$message
    );
  }
  hide() {
    this.$container.removeClass("msg-fade-in").addClass("msg-fade-out");

    this.$container.one("animationend", () => {
      this.$container.hide();
      this.$container.removeClass("msg-fade-out");
    });
  }

  /**
   * constructor method to initalize html
   */

  update(message, msgTitle, cssClass = "") {
    this.msgData.$name.text(msgTitle);
    this.msgData.$message.text(message);

    if (cssClass) {
      this.cssClass = cssClass;
      this.$container.removeClass(this.cssClass).addClass(cssClass);
    }
  }
  /**
   * @param {string} message - the message to display
   * @param {string} name - the title of the message
   * @param {string} cssClass - the new class to apply to the
   * container (e.g success-msg, error-msg)
   */
  show(message, name, cssClass = "") {
    this.update(message, name, cssClass);
    this.$container.show();
    this.$container.removeClass("msg-fade-out").addClass("msg-fade-in");
  }
}


