document.addEventListener("DOMContentLoaded", function() {
    var cpuUsageData = JSON.parse(document.getElementById("cpuUsageData").textContent);
    var memoryUsageData = JSON.parse(document.getElementById("memoryUsageData").textContent);

    if (!Array.isArray(cpuUsageData)) {
        console.error("CPU Usage Data is not an array: ", cpuUsageData);
        cpuUsageData = [];
    }

    if (!Array.isArray(memoryUsageData)) {
        console.error("Memory Usage Data is not an array: ", memoryUsageData);
        memoryUsageData = [];
    }

    var ctxCpu = document.getElementById('cpuUsageChart').getContext('2d');
    var cpuUsageChart = new Chart(ctxCpu, {
        type: 'bar',
        data: {
            labels: cpuUsageData.map(item => item.instance),
            datasets: [{
                label: 'CPU Usage (%)',
                data: cpuUsageData.map(item => item.cpu_usage),
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

    var ctxMemory = document.getElementById('memoryUsageChart').getContext('2d');
    var memoryUsageChart = new Chart(ctxMemory, {
        type: 'bar',
        data: {
            labels: memoryUsageData.map(item => item.instance),
            datasets: [{
                label: 'Memory Usage (%)',
                data: memoryUsageData.map(item => item.memory_usage),
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
});
