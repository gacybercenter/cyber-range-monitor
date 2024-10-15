$(document).ready(function () {
  $(".menu > li > a").click(function (e) {
    var $submenu = $(this).next(".sub-menu");
    if ($submenu.length) {
      e.preventDefault();
      var $parentLi = $(this).parent();

      if ($(".sidebar").hasClass("collapsed")) {
        $(".sidebar").removeClass("collapsed");
      }

      $parentLi.toggleClass("active");
      $submenu.slideToggle();
      $parentLi.siblings().removeClass("active").find(".sub-menu").slideUp();
    }
  });

  $(".menu-btn").click(function () {
    $(".sidebar").toggleClass("collapsed");
  });

  $(".icon").hover(
    function () {
      $(this).css("color", "var(--hm-green)");
    },
    function () {
      $(this).css("color", "");
    }
  );
});
