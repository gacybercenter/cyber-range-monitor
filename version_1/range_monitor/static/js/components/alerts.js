// static/js/components/alerts.js

/**
 * adds the UI events and effects
 * for the alert bar if it's found
 * (i.e an element has id of alertContent)
 */

// WIP: modularizing alert bar
export function animateAlerts() {
  const $alertContent = $("#alertContent");
  if ($alertContent.length === 0) {
    console.log("AlertBarInfo: No alert content or alert bar was found");
    return;
  }
  
  $("#alertToggler").on("click", function () {
    $(this).toggleClass("rotated");
    $alertContent.toggleClass("show");
  });

  $(".alert-item").each(function () {
    $(this).addClass("show");
  });
}
function removeAlertBar() {
  $(".alert-container").remove();
}

function addAlert(message) {
  const $alerts = $("#alertList");
  const [noAlerts, $noAlert] = fetchAlertStatus();
  if (noAlerts) {
    $noAlert.remove();
  }
  


}

function fetchAlertStatus() {
  const $noAlert = $("#noAlerts");
  return [$noAlert.length === 0, $noAlert];
}
