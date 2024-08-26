function updateSlideshow() {
  fetch("api/slideshow_data")
    .then((response) => response.json())
    .then((data) => {
        console.log(data);
      var url = data.url;
      var token = data.token;
      var link = `${url}?token=${token}`;
      const newWindow = window.open(link, "_blank");
      if (!newWindow) {
        console.log("Window was blocked by popup blocker");
      }
    });
}

updateSlideshow();
setInterval(updateSlideshow, 5000);
