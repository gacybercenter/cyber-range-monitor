var xValues = []
var yValues = []
var barColors = [
  "#7de074",
  "#d7e074",
  "#e0bc74",
  "#e08f74",
  "#e07486",
];
const ctx = document.getElementById('saltChart').getContext('2d');
let saltChart = new Chart(ctx, {
  type: "doughnut",
  data: {
    labels: xValues,
    datasets: [{
      backgroundColor: barColors,
      data: yValues
    }]
  },
  options: {
    title: {
      display: true,
      text: "Minion Types"
    }
  }
});


function updateGraph() {
  fetch('api/minion_data')
    .then(response => response.json())
    .then(data => {
      const xvalue = data.x;
      const yvalue = data.y;
      const bgColors = [];
      for (let i = 0; i < xvalue.length; i++) {
        bgColors.push(barColors[i % barColors.length]);
      }
      saltChart.data.labels = xvalue;
      saltChart.data.datasets[0].data = yvalue;
      saltChart.data.datasets[0].backgroundColor = bgColors;
      saltChart.update();
    })
    .catch(error => {
      console.error('Error fetching the data:', error);
    });
}

function setChartType(newType) {
  saltChart.destroy();
  saltChart = new Chart(ctx, {
    type: newType,
    data: {
      labels: xValues,
      datasets: [{
        backgroundColor: barColors,
        data: yValues
      }]
    },
    options: getChartOptions(newType)
  });
  updateGraph();
}

function getChartOptions(chartType){
  switch(chartType){
    case 'bar':
      return {
        scales: {
          yAxes: [{ticks: {beginAtZero: true}}],
          xAxes: [{ticks: {beginAtZero: true}}]
        },
        title: {
          display: true,
          text: "Minion Types"
        },
        legend: {
          display: false
        }
      };
    case 'polarArea':
      return {
        title: {
          display: true,
          text: "Minion Types"
        },
        scale: {
          display: false
        }
      };
    default:
      return {
        title: {
          display: true,
          text: "Minion Types"
        }
      };
  }
}

document.getElementById('pieButton').addEventListener('click', function() {
  setChartType("doughnut");
});

document.getElementById('polarButton').addEventListener('click', function() {
  setChartType("polarArea");
});

document.getElementById('barButton').addEventListener('click', function() {
  setChartType("bar");
});

updateGraph()
setInterval(updateGraph, 5000);
