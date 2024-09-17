
const inputs = document.querySelectorAll("input");
inputs.forEach((input) => {
  input.addEventListener("focus", function () {
    this.parentElement.style.transform = "translateY(-5px)";
    this.parentElement.style.boxShadow = "0 5px 15px rgba(0, 0, 0, 0.2)";
  });
  input.addEventListener("blur", function () {
    this.parentElement.style.transform = "translateY(0)";
    this.parentElement.style.boxShadow = "none";
  });
});
