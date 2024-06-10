document.addEventListener('DOMContentLoaded', function() {
    var ctxCpu = document.getElementById('cpuUsageChart').getContext('2d');
    var cpuUsageChart = new Chart(ctxCpu, {
        type: 'line',
        data: {
            labels: window.cpuUsageTimes,
            datasets: [{
                label: 'CPU Usage (%)',
                data: window.cpuUsageValues,
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

    var ctxMemory = document.getElementById('memoryUsageChart').getContext('2d');
    var memoryUsageChart = new Chart(ctxMemory, {
        type: 'line',
        data: {
            labels: window.memoryUsageTimes,
            datasets: [{
                label: 'Memory Usage (%)',
                data: window.memoryUsageValues,
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

    var ctxNetwork = document.getElementById('networkTrafficChart').getContext('2d');
    var networkTrafficChart = new Chart(ctxNetwork, {
        type: 'line',
        data: {
            labels: window.networkTrafficTimes,
            datasets: [{
                label: 'Network Traffic (MB)',
                data: window.networkTrafficValues,
                borderColor: 'rgba(255, 206, 86, 1)',
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
