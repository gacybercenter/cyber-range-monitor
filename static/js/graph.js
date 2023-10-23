fetch('/api/graph_data')
    .then(response => response.json())
    .then(data => {
        const ctx = document.getElementById('chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [data.label],
                datasets: [{
                    label: 'Connections',
                    data: [data.value],
                    backgroundColor: 'rgba(0, 123, 255, 0.5)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        ticks: {
                            precision: 0
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
                    const label = updatedData.label;
                    const value = updatedData.value;

                    // Append new label and value to the existing data
                    chart.data.labels.push(label);
                    chart.data.datasets[0].data.push(value);

                    // Remove the oldest label and value if the array exceeds a certain length
                    const maxDataPoints = 12;
                    if (chart.data.labels.length > maxDataPoints) {
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                    }

                    chart.update();

                    // Schedule the next update
                    setTimeout(updateGraph, 3000);
                });
        }

        setTimeout(updateGraph, 3000);
    });