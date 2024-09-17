document.addEventListener("DOMContentLoaded", () => {
    const bg_div = document.querySelector(".background");
    function createStars() {
        const star = document.createElement("div")
        star.style.position = "absolute";
        star.style.width = "2px";
        star.style.height = "2px";
        star.style.backgroundColor = "white";
        star.style.borderRadius = "50%";
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animation = `float ${3 + Math.random() * 4}s ease-in-out`;
        bg_div.appendChild(star);
    }
    for(let i = 0; i < 100; i++) {
        createStars();
    }
});