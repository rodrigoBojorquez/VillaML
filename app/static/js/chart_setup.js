document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('myChart').getContext('2d');

    const myChart = new Chart(ctx, {
        type: 'bar', // o 'line', 'pie', etc.
        data: {
            labels: ['A', 'B', 'C', 'D'], // etiquetas en el eje X
            datasets: [{
                label: 'Ejemplo de datos',
                data: [12, 19, 3, 5], // valores en Y
                borderWidth: 1,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
