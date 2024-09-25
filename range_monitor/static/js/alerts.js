const items = document.querySelectorAll(".alert-item");
const alertContent = document.getElementById("alertContent");

function toggleAlerts(btn) {
  btn.classList.toggle("rotate");
  alertContent.classList.toggle("show");
}

document.addEventListener("DOMContentLoaded", () => {
  items.forEach( (item) => {
    item.classList.add("show");
  });
});