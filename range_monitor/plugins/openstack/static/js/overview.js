document.addEventListener('DOMContentLoaded', function () {
    const cpuUsageElement = document.getElementById('cpuUsageData');
    const memoryUsageElement = document.getElementById('memoryUsageData');

    let cpuUsageData, memoryUsageData;

    try {
        cpuUsageData = JSON.parse(cpuUsageElement.textContent);
        memoryUsageData = JSON.parse(memoryUsageElement.textContent);
    } catch (error) {
        console.error("Error parsing JSON data: ", error);
        return;
    }

    if (!Array.isArray(cpuUsageData)) {
        console.error("CPU Usage Data is not an array:", cpuUsageData);
        return;
    }

    if (!Array.isArray(memoryUsageData)) {
        console.error("Memory Usage Data is not an array:", memoryUsageData);
        return;
    }

    let cpuUsageChart, memoryUsageChart;

    function destroyExistingChart(chart) {
        if (chart) {
            chart.destroy();
        }
    }

    function createChart(ctx, data, label, borderColor) {
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.instance),
                datasets: [{
                    label: label,
                    data: data.map(d => d.cpu_usage),
                    borderColor: borderColor,
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

    const ctxCpu = document.getElementById('cpuUsageChart').getContext('2d');
    destroyExistingChart(cpuUsageChart);
    cpuUsageChart = createChart(ctxCpu, cpuUsageData, 'CPU Usage (%)', 'rgba(75, 192, 192, 1)');

    const ctxMemory = document.getElementById('memoryUsageChart').getContext('2d');
    destroyExistingChart(memoryUsageChart);
    memoryUsageChart = createChart(ctxMemory, memoryUsageData, 'Memory Usage (%)', 'rgba(153, 102, 255, 1)');
});
