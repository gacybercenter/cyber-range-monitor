const apiEndpoint = '/saltstack/api/cpu_temp';
const updateInterval = 5000;


const minionData = {};

const ctx = document.getElementById('temperatureChart').getContext('2d');
const temperatureChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: []
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true
            }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    tooltipFormat: 'HH:mm:ss',
                    unit: 'second'
                },
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
              min: 0,
              max: 65,
              title: {
                  display: true,
                  text: 'Temperature (°C)'
              }
          }
        }
    }
});

async function fetchAndUpdate() {
    try {
        const response = await fetch(apiEndpoint);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        const currentTime = new Date();

        Object.entries(data).forEach(([minionId, temperature]) => {
            if (!minionData[minionId]) {
                minionData[minionId] = { times: [], temperatures: [] };
                temperatureChart.data.datasets.push({
                    label: minionId,
                    data: [],
                    borderColor: (220,88,42),
                    fill: false
                });
            }

            minionData[minionId].times.push(currentTime);
            minionData[minionId].temperatures.push(temperature);

            const dataset = temperatureChart.data.datasets.find(ds => ds.label === minionId);
            dataset.data.push({ x: currentTime, y: temperature });
        });

        if (!temperatureChart.data.labels.includes(currentTime)) {
            temperatureChart.data.labels.push(currentTime);
        }
        temperatureChart.update();
    } catch (error) {
        console.error('Failed to fetch data:', error);
    }
}

setInterval(fetchAndUpdate, updateInterval);