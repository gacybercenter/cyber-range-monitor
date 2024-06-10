var xValues = []
var yValues = []
var barColors = [
  "#7de074",
  "#d7e074",
  "#e0bc74",
  "#e08f74",
  "#e07486",
];
const piechart = new Chart("piechart", {
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
      piechart.data.labels = xvalue;
      piechart.data.datasets[0].data = yvalue;
      piechart.data.datasets[0].backgroundColor = bgColors;
      piechart.update();
    })
    .catch(error => {
      console.error('Error fetching the data:', error);
    });
}

updateGraph()
setInterval(updateGraph, 5000);