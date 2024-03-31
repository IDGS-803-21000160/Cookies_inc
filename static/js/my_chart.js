var ctx = document.getElementById('myChart').getContext('2d');
var earning = document.getElementById('earning').getContext('2d');

const allColors = [
    // 'rgba(153, 102, 255, 1)',
    // 'rgba(255, 159, 64, 1)',
    // 'rgba(75, 192, 192, 1)',
    // 'rgba(255, 0, 0, 1)',     // Red
    // 'rgba(0, 255, 0, 1)',     // Green
    // 'rgba(0, 0, 255, 1)',     // Blue
    // 'rgba(255, 255, 0, 1)',   // Yellow
    // 'rgba(255, 0, 255, 1)',   // Magenta
    // 'rgba(0, 255, 255, 1)'
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)',
    'rgba(255, 99, 132, 1)',
    'rgba(54, 162, 235, 1)',
    'rgba(255, 206, 86, 1)',
    'rgba(75, 192, 192, 1)',
    'rgba(153, 102, 255, 1)',
    'rgba(255, 159, 64, 1)'
];

// CHARTS ---------------------------------------------------------------
var myChart = new Chart(ctx, {
    type: 'polarArea',
    data: {
        datasets: [{
            backgroundColor: allColors
        }]

    },
    options: {
        responsive: true, 
        plugins: {
            title: {
                display: true,
                text: 'Ventas Producto Mensual'
            }
        }
    }
});

var earning = new Chart(earning, {
    type: 'line',
    data: {
        labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
        datasets: [{
            label: 'Distribucion de ventas',
            backgroundColor: allColors,
        }]
    },
    options: {
        responsive: true, 
    }
});

// Function to create charts ---------------------------------------------------------------
function productChart() {
    // Get the selected week number from the input field
    const weekNumber = document.getElementById('monthSelect').value;
    //const weekNumber = 3
    // Make AJAX request to get ventas data for the selected week
    fetch('/get_ventasPr?week_number=' + weekNumber)
        .then(response => response.json())
        .then(data => {
            // Extract data for the chart
            const chartData = data.map(item => {
                return { label: item.nombre, value: item.cantidad };
            });

            // Update myChart object with new data
            myChart.data.labels = chartData.map(item => item.label);
            myChart.data.datasets[0].data = chartData.map(item => item.value);

            // Update the chart
            myChart.update();
            console.log(data);
        })
        .catch(error => console.error('Error:', error));
}

function getVentasAnio() {
    fetch('/getVentasAnio')
        .then(response => response.json())
        .then(data => {
            // Create an array to hold the data for each month
            const chartData = new Array(12).fill(0);

            // Update the data array with the quantity for each month
            data.forEach(item => {
                const monthIndex = parseInt(item.mes) - 1; // Months are 1-indexed in SQL
                chartData[monthIndex] = item.cantidad;
            });

            // Update myChart object with new data
            earning.data.datasets[0].data = chartData;

            // Update the chart
            earning.update();
            console.log(data);
        })
        .catch(error => console.error('Error:', error));
}

// ------------------------------------------------------------------------------------------
// Execute createCharts function when the DOM content is loaded
document.addEventListener('DOMContentLoaded', function () {
    productChart();
    getVentasAnio();
    getProduccion();
});

document.getElementById('monthSelect').addEventListener('change', productChart);