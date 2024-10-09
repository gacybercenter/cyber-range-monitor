// static/js/alerts.js
$(function() {
  const $alertContent = $("#alertContent");  
  $("#alertToggler").on("click", function() {
    $(this).toggleClass("rotated");        
    $alertContent.toggleClass("show");     
  });

  $(".alert-item").each(function() {
    $(this).addClass("show");              
  });
});