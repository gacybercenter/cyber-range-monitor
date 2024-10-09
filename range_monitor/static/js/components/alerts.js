// static/js/components/alerts.js

/**
 * adds the UI events and effects
 * for the alert bar if it's found
 * (i.e an element has id of alertContent) 
*/
export const initAlerts = () => {
  const $alertContent = $("#alertContent");
	if ($alertContent.length === 0) {
		console.log("No alert content found");
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