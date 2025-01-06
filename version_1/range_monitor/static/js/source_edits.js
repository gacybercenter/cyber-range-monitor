$(document).ready(function () {
  const $togglePassword = $(".toggle-password");
  const $passwordInput = $("#password");

  $togglePassword.click(function () {
    const type =
      $passwordInput.attr("type") === "password" ? "text" : "password";
    $passwordInput.attr("type", type);
    $("i", this).toggleClass("fa-eye fa-eye-slash");
  });
  $(".data-field").hover(
    function () {
      $(this).css("boxShadow", "0 0 5px rgba(80, 120, 127, 0.5)");
    },
    function () {
      $(this).css("boxShadow", "none");
    }
  );
});
