// assets/js/charts.js

document.addEventListener('DOMContentLoaded', function() {
    // Subject Chart (Bar Chart)
    const subjectCtx = document.getElementById('subjectChart').getContext('2d');
    new Chart(subjectCtx, {
        type: 'bar',
        data: {
            labels: ['Tamil', 'English', 'Maths', 'Physics', 'Chemistry', 'Biology', 'Comp. Sci'],
            datasets: [
            {
                label: 'Average Score',
                data: [72, 68, 84, 76, 74, 79, 82],
                backgroundColor: [72, 68, 84, 76, 74, 79, 82].map(v => v >= 80 ? '#10B981' : (v >= 50 ? '#F59E0B' : '#EF4444')),
                borderRadius: {topLeft: 8, topRight: 8, bottomLeft: 0, bottomRight: 0},
                barPercentage: 0.6
            },
            {
                label: 'Pass Mark',
                data: [50, 50, 50, 50, 50, 50, 50],
                type: 'line',
                borderColor: 'rgba(148, 163, 184, 0.5)',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0,
                tension: 0.4
            }]
        },
        options: {
            indexAxis: 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0F172A',
                    bodyColor: '#475569',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 12,
                    boxPadding: 6,
                    usePointStyle: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(241, 245, 249, 0.5)', drawBorder: false }
                },
                x: {
                    grid: { display: false, drawBorder: false },
                    ticks: {
                        color: '#64748B',
                        font: { family: 'Inter', size: 11 }
                    }
                }
            }
        }
    });

    // Ratio Chart (Doughnut Chart)
    const ratioCtx = document.getElementById('ratioChart').getContext('2d');
    new Chart(ratioCtx, {
        type: 'doughnut',
        data: {
            labels: ['Pass', 'Fail'],
            datasets: [{
                data: [88, 12],
                backgroundColor: ['#10B981', '#EF4444'],
                hoverOffset: 6,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 25,
                        font: { family: 'Inter', size: 12, weight: '500' },
                        color: '#475569'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0F172A',
                    bodyColor: '#475569',
                    borderColor: '#E2E8F0',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 12
                }
            }
        }
    });
});
