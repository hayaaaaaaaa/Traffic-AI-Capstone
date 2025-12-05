// CHART 1: RESPONSE TIME
const ctx1 = document.getElementById('responseChart').getContext('2d');
new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Trial 1', 'Trial 2', 'Trial 3', 'Average'],
        datasets: [
            {
                label: 'Normal Traffic (sec)',
                data: [1.95, 2.10, 2.05, 2.03],
                backgroundColor: '#456882',
                borderColor: '#DDC3C3',
                borderWidth: 1
            },
            {
                label: 'Ambulance Priority (sec)',
                data: [1.26, 1.42, 1.35, 1.79],
                backgroundColor: '#6B3F69',
                borderColor: '#A376A2',
                borderWidth: 1
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: 'white' } }
        },
        scales: {
            y: { 
                beginAtZero: true, 
                ticks: { color: 'white' },
                title: { display: true, text: 'Time (Seconds)', color: 'white' }
            },
            x: { ticks: { color: 'white' } }
        }
    }
});

// CHART 2: ACCURACY
const ctx2 = document.getElementById('accuracyChart').getContext('2d');
new Chart(ctx2, {
    type: 'line',
    data: {
        labels: ['Trial 1', 'Trial 2', 'Trial 3'],
        datasets: [{
            label: 'System Decision Accuracy (%)',
            data: [62.5, 87.5, 100],
            borderColor: '#00ff00',
            backgroundColor: 'rgba(0, 255, 0, 0.2)',
            tension: 0.3,
            fill: true,
            pointRadius: 8
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: 'white' } }
        },
        scales: {
            y: { 
                min: 0, max: 110,
                ticks: { color: 'white' }
            },
            x: { ticks: { color: 'white' } }
        }
    }
});