// static/js/ui-effects.js
/*
  NOTE
  The typing animation can be applied to any div with the 
  ID of "typedText" and the text you want typed being stored
  in the data-typed-text attribute. 
*/

const sanitizeText = (text) => {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Reusable typing animation function
const typingAnimation = (elementId, typingSpeed = 150, delay = 1000) => {
  const element = document.getElementById(elementId);
  const textToType = element.getAttribute("data-typed-text"); 
  const sanitizedText = sanitizeText(textToType); // sanitization
  element.textContent = ""; 
  let i = 0;
  const type = function () {
    if (i < sanitizedText.length) {
      element.textContent += sanitizedText.charAt(i);
      i++;
      setTimeout(type, typingSpeed);
    }
  }
  setTimeout(type, delay);
}

document.addEventListener("DOMContentLoaded", () => {
  typingAnimation("typedText", 150, 1000);
});