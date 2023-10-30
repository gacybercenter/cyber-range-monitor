fetch('/api/graph_data')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [data.date],
                datasets: [{
                    label: 'Connections',
                    data: [data.conns],
                    color: 'white',
                    backgroundColor: 'rgba(0, 123, 255, 0.5)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1,
                    pointRadius: 1
                }]
            },
            options: {
                scales: {
                    x: {
                        ticks: {
                            color: 'white',
                        }
                    },
                    y: {
                        ticks: {
                            precision: 0,
                            suggestedMin: data.conns - 5,
                            suggestedMax: data.conns + 5,
                            color: 'white',
                        }
                    }
                },
                responsive: true,
                maintainAspectRatio: true
            }
        });

        function updateGraph() {
            fetch('/api/graph_data')
                .then(response => response.json())
                .then(updatedData => {
                    const date = updatedData.date;
                    const conns = updatedData.conns;

                    // Append new label and value to the existing data
                    chart.data.labels.push(date);
                    chart.data.datasets[0].data.push(conns);

                    // Remove the oldest label and value if the array exceeds a certain length
                    const maxDataPoints = 720;
                    if (chart.data.labels.length > maxDataPoints) {
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                    }

                    chart.update();

                    // Schedule the next update
                    setTimeout(updateGraph, 5000);
                });
        }

        setTimeout(updateGraph, 5000);
    });