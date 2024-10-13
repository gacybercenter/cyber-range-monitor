// static/js/components/modal.js

/**
 * Using the id of a Form and a triggger (button)
 * a modal will be created and displayed when the
 * trigger is clicked and will submit the form when
 * the confirm button is clicked.
 * @param {string} formId
 * @param {string} triggerId
 * @returns {Object} modal object with references to the form and trigger jQuery objects
 */
export function createModal(formId, triggerId) {
  const [isValid, modal] = validateModal(formId, triggerId);

  if (!isValid) return;

  addModalEvents(modal);
  return modal;
}
// adds the event listeners to the modal
function addModalEvents({ $trigger, $form }) {
  $trigger.click(function (event) {
    event.preventDefault();
    showModal();
  });

  $(".modal-btn.confirm").click(function (event) {
    event.preventDefault();
    $form.submit();
  });

  $(".modal-btn.cancel").click(function (event) {
    event.preventDefault();
    hideModal();
  });
}
// shows the modal when the trigger is clicked
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
// hides the modal when the cancel button is clicked
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
