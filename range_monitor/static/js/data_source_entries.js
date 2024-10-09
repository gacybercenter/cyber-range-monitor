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
    resetIcons(this);
    toggleIcon($(this));
    $(this).closest("form").submit();
  });

  $(".url-icon").on("click", function () {
    navigator.clipboard.writeText($(this).data("url"));
  });
});
