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
    const date = new Date(label);
    return date.toLocaleString();
});

const updatedHistory = {
    ...historyObject,
    datasets,
    labels,
};

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
                beginAtZero: true,
                type: 'logarithmic', // Set y-axis scale to logarithmic
                ticks: {
                    color: 'white', // Set label color to white
                },
            },
            x: {
                stacked: true,
                ticks: {
                    color: 'white', // Set label color to white
                },
            },
        },
        plugins: {
            tooltip: {
                callbacks: {
                    title: function (context) {
                        return context[0].label;
                    },
                    label: function (context) {
                        return context.parsed.y.toFixed(2) + ' Minutes';
                    },
                },
            },
        },
        legend: {
            labels: {
                color: 'white', // Set legend label text color to white
            },
        },
    },
});