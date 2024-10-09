// static/js/source_edits.js
document.addEventListener("DOMContentLoaded", () => {
  const togglePassword = document.querySelector(".toggle-password");
  const passwordInput = document.getElementById("password");
  // password visibility toggler
  togglePassword.addEventListener("click", function () {
    const type =
      passwordInput.getAttribute("type") === "password" ? "text" : "password";
    passwordInput.setAttribute("type", type);
    this.querySelector("i").classList.toggle("fa-eye");
    this.querySelector("i").classList.toggle("fa-eye-slash");
  });

  const inputs = document.querySelectorAll(".data-field");
  inputs.forEach((input) => {
    input.addEventListener("mouseover", function () {
      this.style.boxShadow = "0 0 5px rgba(80, 120, 127, 0.5)";
    });
    input.addEventListener("mouseout", function () {
      this.style.boxShadow = "none";
    });
  });
});
