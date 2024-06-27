document.addEventListener('DOMContentLoaded', function () {
    function updateOverviewData() {
        fetch('/openstack/api/overview_data')
            .then(response => response.json())
            .then(data => {
                console.log("Updated Overview Data:", data);

                // Update the DOM elements with new data
                document.getElementById('activeInstances').textContent = data.instances_summary.active_instances;
                document.getElementById('totalInstances').textContent = data.instances_summary.total_instances;
                document.getElementById('activeNetworks').textContent = data.networks_summary.active_networks;
                document.getElementById('totalNetworks').textContent = data.networks_summary.total_networks;
            })
            .catch(error => console.error("Error updating overview data:", error));
    }

    // Initial update
    updateOverviewData();

    // Set interval to update every 5 seconds
    setInterval(updateOverviewData, 5000);
});
