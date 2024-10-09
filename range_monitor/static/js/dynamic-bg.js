// static/js/dynamic-bg.js

const starBackgroundConfig = {
  starCount: 150, // change as needed
  starColor: "white",
  minSize: 1,
  maxSize: 3,
  animationDuration: 20, // secs
};

function createContainer() {
  const starContainer = document.createElement("div");
  starContainer.style.position = "absolute";
  starContainer.style.top = "0";
  starContainer.style.left = "0";
  starContainer.style.width = "100%";
  starContainer.style.height = "100%";
  starContainer.style.overflow = "hidden";
  starContainer.style.pointerEvents = "none";
  return starContainer;
}

function createStar(container) {
  const star = document.createElement("div");
  const size =
    Math.random() *
      (starBackgroundConfig.maxSize - starBackgroundConfig.minSize) +
    starBackgroundConfig.minSize;

  star.style.position = "absolute";
  star.style.width = `${size}px`;
  star.style.height = `${size}px`;
  star.style.backgroundColor = starBackgroundConfig.starColor;
  star.style.borderRadius = "50%";
  star.style.top = `${Math.random() * 100}%`;
  star.style.left = `${Math.random() * 100}%`;
  star.style.animation = `twinkle ${
    Math.random() * starBackgroundConfig.animationDuration + 5
  }s infinite,  float ${
    Math.random() * (starBackgroundConfig.animationDuration - 10) + 10
  }s linear infinite`;

  container.appendChild(star);
}

document.addEventListener("DOMContentLoaded", () => {
  const elements = document.querySelectorAll(".star-background");

  elements.forEach((element) => {
    if (getComputedStyle(element).position === "static") {
      element.style.position = "relative";
    }

    const starContainer = createContainer();

    for (let i = 0; i < starBackgroundConfig.starCount; i++) {
      createStar(starContainer);
    }
    element.appendChild(starContainer);
  });

  if (!document.querySelector("#star-animation")) {
    const style = document.createElement("style");
    style.id = "star-animation";
    style.textContent = `
        @keyframes twinkle {
            0%, 100% { 
              opacity: 1; 
            }
            50% { 
              opacity: 0.5; 
            }
        }
        @keyframes float {
            0% {
                transform: translateY(0px);
            }

            50% {
                transform: translateY(-10px);
            }

            100% {
                transform: translateY(0px);
            }
        }
    `;
    document.head.appendChild(style);
  }
});
