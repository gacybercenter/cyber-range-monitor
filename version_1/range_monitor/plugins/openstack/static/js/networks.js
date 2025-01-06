document.addEventListener("DOMContentLoaded", function() {
    const networkLinks = document.querySelectorAll(".network-link");

    networkLinks.forEach(link => {
        link.addEventListener("click", function(event) {
            event.preventDefault();
            const networkId = this.dataset.networkId;
            fetchNetworkDetails(networkId);
        });
    });

    function fetchNetworkDetails(networkId) {
        fetch(`/openstack/networks/${networkId}`)
            .then(response => response.text())
            .then(html => {
                document.getElementById("network-details-container").innerHTML = html;
            })
            .catch(error => {
                console.error("Error fetching network details:", error);
            });
    }
});
