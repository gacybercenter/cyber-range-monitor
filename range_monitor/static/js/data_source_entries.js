document.addEventListener("DOMContentLoaded", function () {
  const icons = document.querySelectorAll(".icon");

  icons.forEach((icon) => {
    icon.addEventListener("click", function () {
      const row = this.closest("tr");
      const hiddenCheckbox = row.querySelector(".datasource-checkbox");

      this.classList.toggle("checked");
      this.classList.toggle("unchecked");
      row.classList.toggle("untoggled");

      if (this.classList.contains("checked")) {
        this.classList.remove("fa-times");
        this.classList.add("fa-check");
        hiddenCheckbox.checked = true;
      } else {
        this.classList.remove("fa-check");
        this.classList.add("fa-times");
        hiddenCheckbox.checked = false;
      }

      // Uncheck all other checkboxes
      icons.forEach((otherIcon) => {
        if (otherIcon !== this && otherIcon.classList.contains("checkbox")) {
          otherIcon.classList.remove("checked");
          otherIcon.classList.add("unchecked");
          otherIcon.classList.remove("fa-check");
          otherIcon.classList.add("fa-times");
          otherIcon.closest("tr").classList.add("untoggled");
          otherIcon
            .closest("tr")
            .querySelector(".datasource-checkbox").checked = false;
        }
      });

      // Submit the form
      this.closest("form").submit();
    });
  });
});
