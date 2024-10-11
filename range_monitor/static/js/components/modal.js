// static/js/components/modal.js
class Modal {
  /**
   * Confirm Dialogue Window that accepts an Id
   * of a form and a trigger element. If the
   * confirmation button is clicked, the form is
   * submitted.
   * @param {string} formId
   * @param {string} triggerId
   */
  constructor(formId, triggerId) {
    const [isValid, modal] = validateModal(formId, triggerId);

    if (!isValid) return;

    this.modal = modal;
    addModalEvents(modal);
  }
}

function showModal() {
  $(".modal-overlay").fadeIn(300, function () {
    $(this).css("opacity", "1");
  });
  $(".modal")
    .css({
      display: "block",
      opacity: 0,
      transform: "translate(-50%, -50%) scale(0.9)",
    })
    .animate(
      {
        opacity: 1,
      },
      300,
      function () {
        $(this).css("transform", "translate(-50%, -50%) scale(1)");
      }
    );
}

function hideModal() {
  $(".modal-overlay").fadeOut(300, function () {
    $(this).css("opacity", "0");
  });
  $(".modal").animate(
    {
      opacity: 0,
    },
    300,
    function () {
      $(this).css({
        display: "none",
        transform: "translate(-50%, -50%) scale(0.9)",
      });
    }
  );
}
function validateModal(formId, triggerId) {
  const modal = {
    $form: $(`#${formId}`),
    $trigger: $(`#${triggerId}`),
  };
  if (modal.$form.length === 0 || modal.$trigger.length === 0) {
    console.error(
      `ModalError: Invalid form or modal trigger id (formId: ${formId}, triggerId: ${triggerId})`
    );
    return [false, null];
  }
  return [true, modal];
}
function addModalEvents({ $trigger, $form }) {
  $trigger.on("click", showModal);

  $(".modal-btn.confirm").on("click", () => {
    $form.submit();
  });

  $(".modal-btn.cancel").on("click", hideModal);
}

// $(document).ready(() => {
//   new Modal("modalForm", "showModal");
// });
