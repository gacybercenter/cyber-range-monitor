// static/js/alerts.js
document.addEventListener("DOMContentLoaded", () => {
  const items = document.querySelectorAll(".alert-item");
  const alertContent = document.getElementById("alertContent");
  const alertToggler = document.getElementById("alertToggler");

  alertToggler.addEventListener("click", () => {
    alertToggler.classList.toggle("rotated");
    alertContent.classList.toggle("show");
  });

  items.forEach((item) => {
    item.classList.add("show");
  });
});
