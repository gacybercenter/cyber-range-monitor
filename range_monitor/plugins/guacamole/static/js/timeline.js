var timelineDiv = document.getElementById("timeline");
var historyAttribute = timelineDiv.getAttribute("history");
var historyObject = JSON.parse(historyAttribute);

console.log(historyObject);

const datasets = historyObject.datasets.map((dataset, index) => ({
    ...dataset,
    backgroundColor: getBackgroundColor(index),
    borderColor: getBorderColor(index),
    borderWidth: 1,
}));

const labels = historyObject.labels.map((label) => {
    return new Date(label);
});

const updatedHistory = {
    datasets,
    labels,
};

console.log(updatedHistory);

function getBackgroundColor(index) {
    // Return different background color for each label
    const colors = [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 206, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)',
        'rgba(153, 102, 255, 0.5)',
        'rgba(255, 159, 64, 0.5)'
    ];
    return colors[index % colors.length];
}

function getBorderColor(index) {
    // Return different border color for each label
    const colors = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
    ];
    return colors[index % colors.length];
}

var ctx = document.getElementById('timeline').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: updatedHistory,
    options: {
        scales: {
            y: {
                type: 'logarithmic',
                ticks: {
                    color: 'white',
                    callback: function (value, index, values) {
                        return formatDuration(value);
                    },
                },
                beginAtZero: true,
            },
            x: {
                type: 'time', // Use time scale for x-axis
                time: {
                    unit: 'day', // Display labels by month
                    displayFormats: {
                        day: 'dd MMM yyyy', // Format the month labels as 'MMM YYYY' (e.g., Jan 2022)
                    },
                },
                stacked: true,
                ticks: {
                    color: 'white', // Set label color to white
                },
                barThickness: 10
            },
        },
        plugins: {
            tooltip: {
                callbacks: {
                    title: function (context) {
                        return context[0].label;
                    },
                    label: function (context) {
                        const value = context.parsed.y;
                        return formatDuration(value);
                    },
                },
            },
            zoom: {
                pan: {
                    enabled: true, // Enable panning
                    mode: 'x', // Enable panning in x direction
                    modifierKey: 'ctrl', // Enable panning with alt key
                },
                limits: {
                    
                },
                zoom: {
                    pinch: {
                        enabled: true // Enable zooming with pinch gesture on touch devices
                    },
                    wheel: {
                        enabled: true // Enable zooming with mouse wheel
                    },
                    drag: {
                        enabled: false // Enable dragging
                    },
                    mode: 'x', // Enable zooming in x direction
                },
                
            }
        },
        legend: {
            labels: {
                color: 'white', // Set legend label text color to white
            },
        },
        barThickness: 8
    },
});

function formatDuration(duration) {
    durationString = ''
    const days = Math.floor(duration / 86400000);
    if (days > 0) {
      durationString += `${days}d `;
      duration -= days * 86400000;
    }
    const hours = Math.floor(duration / 3600000);
    if (hours > 0) {
        durationString += `${hours}h `;
        duration -= hours * 3600000;
    }
    const minutes = Math.floor(duration / 60000);
    if (minutes > 0) {
        durationString += `${minutes}m `;
        duration -= minutes * 60000;
    }
    const seconds = Math.floor(duration / 1000);
    if (seconds > 0) {
        durationString += `${seconds}s `;
        duration -= seconds * 1000;
    }

    return durationString;
  }
