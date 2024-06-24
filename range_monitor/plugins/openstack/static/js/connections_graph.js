document.addEventListener("DOMContentLoaded", function() {
    var connectionsGraphData = JSON.parse(document.getElementById("connectionsGraphData").textContent);

    var ctxConnections = document.getElementById('connectionsGraphChart').getContext('2d');
    var connectionsGraphChart = new Chart(ctxConnections, {
        type: 'bar',
        data: {
            labels: connectionsGraphData.map(item => item.instance),
            datasets: [{
                label: 'Active Connections',
                data: connectionsGraphData.map(item => item.active_connections || 0),  // Ensure 0 is shown if no data
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
