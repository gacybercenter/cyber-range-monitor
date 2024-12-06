// todo: refine this and the navbar, 
// make canvas for guac, redesign nodes on topology 
$(document).ready(function () {
  $(".menu-link").click(function (e) {
    var $submenu = $(this).next(".sub-menu");
    if ($submenu.length) {
      e.preventDefault();
      var $parentLi = $(this).parent();

      if ($(".sidebar").hasClass("collapsed")) {
        $(".sidebar").removeClass("collapsed");
      }

      $parentLi.toggleClass("active");
      $submenu.slideToggle();
      
      $parentLi
        .siblings()
        .removeClass("active")
        .find(".sub-menu")
        .slideUp();
    }
  });

  $(".nav-toggler").click(function () {
    $(".sidebar").toggleClass("collapsed");
  });
});
