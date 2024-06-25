document.addEventListener('DOMContentLoaded', function () {
    const cpuUsageDataElement = document.getElementById('cpuUsageData');
    const memoryUsageDataElement = document.getElementById('memoryUsageData');

    if (cpuUsageDataElement) {
        try {
            const cpuUsageData = JSON.parse(cpuUsageDataElement.textContent);
            if (!Array.isArray(cpuUsageData)) {
                console.error("CPU Usage Data is not an array:", cpuUsageData);
            } else {
                renderChart('cpuUsageChart', 'CPU Usage', cpuUsageData, 'cpu_usage');
            }
        } catch (e) {
            console.error("Error parsing CPU usage data:", e);
        }
    }

    if (memoryUsageDataElement) {
        try {
            const memoryUsageData = JSON.parse(memoryUsageDataElement.textContent);
            if (!Array.isArray(memoryUsageData)) {
                console.error("Memory Usage Data is not an array:", memoryUsageData);
            } else {
                renderChart('memoryUsageChart', 'Memory Usage', memoryUsageData, 'memory_usage');
            }
        } catch (e) {
            console.error("Error parsing memory usage data:", e);
        }
    }
});

function renderChart(elementId, label, data, key) {
    const ctx = document.getElementById(elementId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(d => d.instance_name),
            datasets: [{
                label: label,
                data: data.map(d => d[key]),
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
}
