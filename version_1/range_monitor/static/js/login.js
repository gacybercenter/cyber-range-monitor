import { StarBackground } from "./effects/star-bg.js";
import { ToggleMessage } from "./components/toggle_msg.js";

$(document).ready(function () {
  StarBackground.initalize();
  let errMsg;
  try {
    errMsg = new ToggleMessage("error-msg");
  } catch (error) {
    console.error(error);
  }
  ajaxLoginWithError(errMsg);
});

function ajaxLoginWithError(errMsg) {
  $("#loginForm").on("submit", function (e) {
    e.preventDefault();
    var formData = {
      username: $("#username").val(),
      password: $("#password").val(),
    };
    $.ajax({
      type: "POST",
      url: "/auth/login",
      data: formData,
      dataType: "json",
      success: function (response) {
        if (response.success) {
          window.location.href = response.redirect;
        } else {
          if (errMsg) {
            errMsg.show("Invalid Credentials Provided", "Login Error:");
          }
        }
      },
      error: function (response) {
        if (errMsg) {
          errMsg.show("Oops something went wrong...", "Internal Error: ");
        }
      },
    });
  });
}
