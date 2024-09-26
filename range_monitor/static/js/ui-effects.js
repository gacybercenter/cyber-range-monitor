function sanitizeText(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Reusable typing animation function
function startTypingFromAttribute(elementId, typingSpeed = 150, delay = 1000) {
  const element = document.getElementById(elementId);
  const textToType = element.getAttribute("data-typed-text"); 
  const sanitizedText = sanitizeText(textToType); // sanitization
  element.textContent = ""; 
  let i = 0;
  function type() {
    if (i < sanitizedText.length) {
      element.textContent += sanitizedText.charAt(i);
      i++;
      setTimeout(type, typingSpeed);
    }
  }

  setTimeout(type, delay);
}

document.addEventListener("DOMContentLoaded", () => {
  startTypingFromAttribute("typedText", 150, 1000);
});