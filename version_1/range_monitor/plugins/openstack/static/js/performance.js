document.addEventListener('DOMContentLoaded', function () {
    function updatePerformanceData() {
        fetch('/openstack/api/performance_data')
            .then(response => response.json())
            .then(data => {
                console.log("Updated Performance Data:", data);

                // Update CPU usage chart
                if (cpuUsageChart) {
                    updateChart(cpuUsageChart, data.cpu_usage, 'cpu_usage');
                }

                // Update Memory usage chart
                if (memoryUsageChart) {
                    updateChart(memoryUsageChart, data.memory_usage, 'memory_usage');
                }
            })
            .catch(error => console.error("Error updating performance data:", error));
    }

    function updateChart(chart, data, key) {
        chart.data.labels = data.map(d => d.instance_name);
        chart.data.datasets[0].data = data.map(d => d[key]);
        chart.update();
    }

    // Initialize the charts
    const cpuCtx = document.getElementById('cpuUsageChart').getContext('2d');
    const cpuUsageChart = new Chart(cpuCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'CPU Usage',
                data: [],
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
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

    const memoryCtx = document.getElementById('memoryUsageChart').getContext('2d');
    const memoryUsageChart = new Chart(memoryCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Memory Usage',
                data: [],
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
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

    // Initial update
    updatePerformanceData();

    // Set interval to update every 5 seconds
    setInterval(updatePerformanceData, 5000);
});
