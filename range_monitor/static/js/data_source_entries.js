// static/js/data_source_entries.js

/*
  TODO: Now that we are using jQuery make 
  this ajax
*/
$(function () {
  const $icons = $(".icon");

  const resetIcons = (toggledIcon) => {
    $icons
      .not(toggledIcon)
      .removeClass("fa-check checked")
      .addClass("fa-times unchecked")
      .closest("form")
      .find(".datasource-checkbox")
      .prop("checked", false);
  };

  const toggleIcon = ($icon) => {
    const $checkbox = $icon.closest("form").find(".datasource-checkbox");
    $icon.toggleClass("fa-check checked fa-times unchecked");
    $checkbox.prop("checked", !$checkbox.prop("checked"));
  };

  $icons.on("click", function () {
    const $form = $(this).closest("form");
    const url = $form.attr("action");
    const formData = $form.serialize();
    resetIcons($(this));
    toggleIcon($(this));
    $.ajax({
      type: "POST",
      url: url,
      data: formData,
      success: function (response) {
        if (response.success) {
          console.log("Update successful");
        } else {
          console.error("Update failed: ", response.error);
        }
      },
      error: function () {
        console.error("Error updating");
      },
    });
  });

  $(".url-icon").on("click", function () {
    navigator.clipboard.writeText($(this).data("url"));
  });
});


