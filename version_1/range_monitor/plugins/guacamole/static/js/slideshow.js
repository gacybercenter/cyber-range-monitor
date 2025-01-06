const REFRESH = 15000;

var slideshow = true;
var pause = false;
var interactive = false;
var previousLink = null;
var previousUuid = null;
var updateID = null;

const toggleSlideshowButton = document.getElementById(
  "toggle-slideshow-button"
);
const togglePauseButton = document.getElementById(
  "toggle-pause-button"
);
const toggleInteractiveButton = document.getElementById(
  "toggle-interactive-button"
);

const slideshowIframe = document.getElementById("slideshow-iframe");
slideshowIframe.style.pointerEvents = "none";

function toggleSlideshow() {
  slideshow = !slideshow;
  toggleSlideshowButton.textContent = slideshow
    ? "Dashboard Mode"
    : "Slideshow Mode";

  clearInterval(updateID);
  updateSlideshow();
  updateID = setInterval(updateSlideshow, REFRESH)
}

function togglePause() {
  pause = !pause;
  togglePauseButton.textContent = pause
    ? "Resume Update"
    : "Pause Update";

  if (!pause) {
    clearInterval(updateID);
    updateSlideshow();
    updateID = setInterval(updateSlideshow, REFRESH)
  } else {
    clearInterval(updateID);
  }
}

function toggleInteractive() {
  interactive = !interactive;
  slideshowIframe.style.pointerEvents = interactive ? "auto" : "none";
  toggleInteractiveButton.textContent = interactive
    ? "Disable Interactivity"
    : "Enable Interactivity";
}

function updateSlideshow() {
  slideshowIframe.src = "";
  fetch("api/slideshow_data")
    .then((response) => response.json())
    .then((data) => {
      // console.log(data);
      var url = data.url;
      var token = data.token;
      var parts = url.split("/client/");
      var link = `${url}?token=${token}`;

      if (parts.length < 2) {
        return;
      }

      if (slideshow === true) {
        // slideshowIframe.contentWindow.location.reload();
        var prefix = parts[0];
        var uuids = parts[1].split(".");

        // Remove the previous UUID if it exists
        let previousUuidIndex = uuids.indexOf(previousUuid);
        if (previousUuidIndex !== -1 && uuids.length > 1) {
          uuids.splice(previousUuidIndex, 1);
        }

        // Add a new UUID if the list is not empty
        let uuid = uuids[Math.floor(Math.random() * uuids.length)];
        previousUuid = uuid;

        url = `${prefix}/client/${previousUuid}`;
        link = `${url}?token=${token}`;
      }

      slideshowIframe.src = link;
      previousLink = link;
    });
}

updateSlideshow();
updateID = setInterval(updateSlideshow, REFRESH);
