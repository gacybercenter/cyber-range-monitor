// Get modal elements
let networkModal = document.getElementById("networkModal");
let serverModal = document.getElementById("serverModal");

// Get button elements
let networkBtn = document.getElementById("networkSummaryBtn");
let serverBtn = document.getElementById("serverSummaryBtn");

// Get close elements
let closeNetwork = document.getElementById("closeNetwork");
let closeServer = document.getElementById("closeServer");

// Show modals on button click
networkBtn.onclick = function() {
    networkModal.style.display = "block";
}

serverBtn.onclick = function() {
    serverModal.style.display = "block";
}

// Close modals when close button is clicked
closeNetwork.onclick = function() {
    networkModal.style.display = "none";
}

closeServer.onclick = function() {
    serverModal.style.display = "none";
}

// Close modals when clicking outside the modal
window.onclick = function(event) {
    if (event.target == networkModal) {
        networkModal.style.display = "none";
    }
    if (event.target == serverModal) {
        serverModal.style.display = "none";
    }
}
