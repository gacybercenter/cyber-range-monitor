const ctx = document.getElementById('chart').getContext('2d');
const conns_container = document.getElementById('active-conns-container');

const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Connections',
            data: [],
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
                    color: 'white',
                }
            }
        },
        responsive: true,
        maintainAspectRatio: true
    }
});

updateGraph()
setInterval(updateGraph, 5000);

function updateGraph() {
    fetch('api/conns_data')
        .then(response => response.json())
        .then(data => {
            const date = data.date;
            const conns = data.conns
            const amount = Object.keys(conns).length
            console.log(data.conns)
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
            updateActiveConns(conns)
        });
}


function updateActiveConns(activeConns) {
    const connList = document.getElementById('active-conns-container');
    connList.innerHTML = '';
    const groups = [];

    activeConns.forEach(conn => {
        // Extract all prefixes of the connection
        const connection = conn.connection;
        for (let i = 1; i <= connection.length; i++) {
            const prefix = connection.split('.')[0] || "None";
            if (!groups.includes(prefix)) {
                groups.push(prefix);
            }
        }
    });

    // Create <ul> items for each prefix and associate connections
    groups.forEach(prefix => {
        const column = document.createElement('div');
        column.classList.add('column');
        column.innerHTML = `<h2>${prefix}</h2>`;
        const ul = document.createElement('ul');
        ul.classList.add('connections');
        column.appendChild(ul);

        activeConns.forEach(conn => {
            if (conn.connection.startsWith(prefix)) {
                const connItem = document.createElement('li');
                connItem.textContent = `- ${prefix}${conn.connection.substring(prefix.length)} (${conn.username})`;
                ul.appendChild(connItem);
            }
        });

        connList.appendChild(column);
    });
}