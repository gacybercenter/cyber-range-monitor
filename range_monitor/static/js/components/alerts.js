// static/js/components/alerts.js

/**
 * adds the UI events and effects
 * for the alert bar if it's found
 * (i.e an element has id of alertContent)
 */

// WIP: modularizing alert bar
function initAlertBar() {
  const $alertContent = $("#alertContent");
  if ($alertContent.length === 0) {
    console.log("No alert content or alert bar was found");
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
function alertBarExists() {
	return $("#alertContent").length > 0;
}
function deleteAlertBar() {
  $(".alert-container").remove();
}
function getAlertCount() {
  return $(".alert-item").length;
}
function getAlerts() {
  return $(".alert-item")
    .map(function () {
      return $(this).text();
    })
    .get();
}
function replayBellShake(element, className) {
  const bell = $("#alertBell");
	bell.removeClass("shake");
  void bell.get(0).offsetWidth;
  /* chat-gpt says doing line of code above -^
   * "forces reflow by accessing the offsetWidth
   * (this makes the browser "forget" the removed class)" 
  */
  bell.addClass("shake");
}
// function addAlert(message) {
//   const $alertContent = $("#alertContent");
//   if ($alertContent.length === 0) {
//     console.log("No alert content or alert bar was found");
//     return;
//   }
//   const $alerts = $(".alert-list li");
// 	/* 1 alert means their were no alerts and the 
// 	 * "No alerts to display message" is the only ".alert-item"
// 	 * or <li>
// 	*/
// 	const alertNum = 
// 	if($alerts.length === 1) {
// 		$alerts.first().remove(); 
//   }
	




// }