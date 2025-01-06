document.addEventListener('DOMContentLoaded', function () {
    function updateActiveConnections() {
        fetch('/openstack/api/active_connections_data')
            .then(response => response.json())
            .then(data => {
                console.log("Updated Active Connections Data:", data);

                // Clear existing data
                const connectionsContainer = document.getElementById('connectionsContainer');
                connectionsContainer.innerHTML = '';

                // Populate with new data
                data.forEach(connection => {
                    const button = document.createElement('button');
                    button.textContent = connection.instance;
                    button.classList.add('btn', 'btn-primary', 'instance-button');
                    button.setAttribute('data-instance', connection.instance);

                    // Append button to container
                    connectionsContainer.appendChild(button);
                });

                // Add event listeners to buttons
                document.querySelectorAll('.instance-button').forEach(button => {
                    button.addEventListener('click', function () {
                        const instance = this.getAttribute('data-instance');
                        fetchInstanceDetails(instance);
                    });
                });
            })
            .catch(error => console.error("Error updating active connections data:", error));
    }

    function fetchInstanceDetails(instance) {
        fetch(`/openstack/api/instance_details?instance=${encodeURIComponent(instance)}`)
            .then(response => response.json())
            .then(details => {
                const detailsContainer = document.getElementById('instanceDetailsContainer');
                detailsContainer.innerHTML = `
                    <h3>Details for ${instance}</h3>
                    <p><strong>Instance Name:</strong> ${details.instance_name}</p>
                    <p><strong>Project:</strong> ${details.project}</p>
                    <p><strong>Status:</strong> ${details.status}</p>
                    <p><strong>Created:</strong> ${details.created}</p>
                    <p><strong>Updated:</strong> ${details.updated}</p>
                `;
            })
            .catch(error => console.error("Error fetching instance details:", error));
    }

    // Initial update
    updateActiveConnections();

    // Set interval to update every 5 seconds
    setInterval(updateActiveConnections, 5000);
});
