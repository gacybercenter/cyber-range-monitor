const apiEndpoint = '/saltstack/api/cpu_temp';
const updateInterval = 5000;


const minionData = {};
const machineColors = {
  compute: 'rgba(255, 99, 132, 1)',
  controller: 'rgba(54, 162, 235, 1)',
  controllerv2: 'rgba(0, 243, 255, 1)',
  storage: 'rgba(235, 242, 0, 1)'
};
const dashStyles = {
  compute: [5, 2, 5, 10],
  controller: [3, 3],
  controllerv2: [5, 5],
  storage: [10, 5, 2, 5]
};

const ctx = document.getElementById('temperatureChart').getContext('2d');
const temperatureChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: []
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        enabled: true,
        intersect: false,
        mode: 'nearest',
        position: 'nearest'
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          tooltipFormat: 'HH:mm:ss',
          unit: 'second'
        },
        ticks: {
          color: 'white'
        }
      },
      y: {
        min: 0,
        max: 100,
        ticks: {
          color: 'white'
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
      const machineType = minionId.split('-')[0];
      const lineColor = machineColors[machineType] || 'rgba(128, 128, 128, 1)';
      const dashStyle = dashStyles[machineType] || [];

      if (!minionData[minionId]) {
        minionData[minionId] = { times: [], temperatures: [] };
        temperatureChart.data.datasets.push({
          label: minionId,
          data: [],
          borderColor: lineColor,
          borderDash: dashStyle,
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
    console.log('Updating chart with data:', minionData);
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }
}

setInterval(fetchAndUpdate, updateInterval);