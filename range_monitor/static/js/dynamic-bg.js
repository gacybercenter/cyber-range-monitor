document.addEventListener("DOMContentLoaded", () => {
  const starBg = document.querySelector(".star-background");

  function createStar() {
    const star = document.createElement("div");
    star.className = "star";
    star.style.top = Math.random() * 100 + "%";
    star.style.left = Math.random() * 100 + "%";

    const size = Math.random() * 3 + 1;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;

    const duration = Math.random() * 3 + 2;
    star.style.animationDuration = `${duration}s`;
    star.style.animationDelay = `-${duration}s`;

    const xEnd = 100 * (Math.random() - 0.5) * 2;
    const yEnd = 150 * (Math.random() - 0.5) * 2;
    star.style.animationName = "float";
    star.style.animationTimingFunction = "linear";
    star.style.animationIterationCount = "infinite";
    star.style.animationDirection = "alternate";
    starBg.appendChild(star);
  }

  for (let i = 0; i < 50; i++) {
    createStar();
  }
});
