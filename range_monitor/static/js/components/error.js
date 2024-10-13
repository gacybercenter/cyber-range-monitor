// static/js/components/error.js

export class ErrorMessage {
  /**
   * Finds the error container (#errorContainer) and
   * creates the error message html
   */
  constructor() {
    this.data = {
      $container: $("#errorContainer"),
    };

    if (this.data.$container.length === 0) {
      throw new Error("Error container not found");
    }

    this.generate();
  }

  generate() {
    const { $close, $errorName, $message } = createErrorHTML();

    this.data = {
      ...this.data,
      $close,
      $errorName,
      $message,
    };

    this.data.$close.on("click", () => {
      this.hide();
    });

    this.data.$container.append($close).append($errorName).append($message);
  }

  hide() {
    if (this.data.$container) {
      this.data.$container.fadeOut(500);
    }
  }

  update(message, errorName = "Error:") {
    this.data.$errorName.text(errorName);
    this.data.$message.text(message);
  }

  show(message, errorName = "Error:") {
    this.update(message, errorName);
    this.data.$container.fadeIn(500);
  }
}

function createErrorHTML() {
  const $close = $("<span>", {
    class: "close-btn",
    html: '<i class="fas fa-times"></i>',
  });
  const $errorName = $("<strong>", { id: "errorName" });
  const $message = $("<p>", { id: "errorText" });

  return {
    $close,
    $errorName,
    $message,
  };
}
