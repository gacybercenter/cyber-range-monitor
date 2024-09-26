document.addEventListener("DOMContentLoaded", function () {
  const icons = document.querySelectorAll(".icon");
  const urlIcons = document.querySelectorAll(".url-icon");

  function resetIcons(toggledIcon) {
    icons.forEach((icon) => {
      if (icon !== toggledIcon) {
        const checkbox = icon
          .closest("form")
          .querySelector(".datasource-checkbox");
        icon.classList.remove("fa-check", "checked");
        icon.classList.add("fa-times", "unchecked");
        checkbox.checked = false;
      }
    });
  }
  function toggleIcon(icon) {
    const checkbox = icon.closest("form").querySelector(".datasource-checkbox");
    if (!checkbox.checked) {
      icon.classList.remove("fa-times", "unchecked");
      icon.classList.add("fa-check", "checked");
      checkbox.checked = true;
    } else {
      icon.classList.remove("fa-check", "checked");
      icon.classList.add("fa-times", "unchecked");
      checkbox.checked = false;
    }
  }

  function submitForm(icon) {
    icon.closest("form").submit();
  }

  icons.forEach((icon) => {
    icon.addEventListener("click", function () {
      resetIcons(this);
      toggleIcon(this);
      submitForm(this);
    });
  });

  if (urlIcons !== null) {
    urlIcons.forEach((icon) => {
      icon.addEventListener("click", () => {
        const url = icon.getAttribute("data-url");
        navigator.clipboard.writeText(url);
      });
    });
  }
});
