const ctx = document.getElementById('chart').getContext('2d');

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Connections',
            data: [],
            color: 'white',
            backgroundColor: 'rgba(0, 123, 255, 0.75)',
            borderColor: 'rgba(0, 123, 255, 1)',
            borderWidth: 1,
            pointRadius: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                ticks: {
                    color: 'white',
                }
            },
            y: {
                ticks: {
                    precision: 0,
                    color: 'white',
                }
            }
        },
    }
});

function updateGraph() {
    fetch('api/conns_data')
        .then(response => response.json())
        .then(data => {
            const date = data.date;
            const conns = data.conns
            const amount = Object.keys(conns).length

            // Append new label and value to the existing data
            chart.data.labels.push(date);
            chart.data.datasets[0].data.push(amount);

            // Remove the oldest label and value if the array exceeds a certain length
            const maxDataPoints = 720;
            if (chart.data.labels.length > maxDataPoints) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }

            chart.update();
        });
}

updateGraph()
setInterval(updateGraph, 5000);
