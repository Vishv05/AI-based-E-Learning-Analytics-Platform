/*
   AI E-Learning Analytics Platform
   Chart.js Visualization Functions
*/

// Chart.js Global Configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 15;

// Color Palette
const colors = {
    primary: '#667eea',
    secondary: '#764ba2',
    success: '#2ecc71',
    danger: '#e74c3c',
    warning: '#f39c12',
    info: '#3498db',
    gradient: {
        primary: ['rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'],
        success: ['rgba(46, 204, 113, 0.8)', 'rgba(39, 174, 96, 0.8)'],
        danger: ['rgba(231, 76, 60, 0.8)', 'rgba(192, 57, 43, 0.8)'],
        info: ['rgba(52, 152, 219, 0.8)', 'rgba(41, 128, 185, 0.8)']
    }
};

// Dashboard Charts

function loadProgressChart() {
    fetch('/api/student-progress')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('progressChart').getContext('2d');
            
            const datasets = data.slice(0, 5).map((student, index) => {
                const colorPalette = [
                    'rgb(102, 126, 234)',
                    'rgb(231, 76, 60)',
                    'rgb(46, 204, 113)',
                    'rgb(243, 156, 18)',
                    'rgb(52, 152, 219)'
                ];
                
                return {
                    label: `Student ${student.student_id}`,
                    data: student.progress,
                    borderColor: colorPalette[index],
                    backgroundColor: colorPalette[index] + '20',
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true
                };
            });
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'],
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2.5,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Course Progress (%)',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        })
        .catch(error => console.error('Error loading progress chart:', error));
}

function loadScoreDistribution() {
    fetch('/api/quiz-scores')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('scoreDistributionChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.counts,
                        backgroundColor: [
                            'rgba(231, 76, 60, 0.8)',
                            'rgba(243, 156, 18, 0.8)',
                            'rgba(241, 196, 15, 0.8)',
                            'rgba(52, 152, 219, 0.8)',
                            'rgba(46, 204, 113, 0.8)',
                            'rgba(39, 174, 96, 0.8)'
                        ],
                        borderWidth: 3,
                        borderColor: '#fff',
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 1.5,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 15,
                                font: { size: 11 }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} students (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading score distribution:', error));
}

function loadEngagementTrend() {
    fetch('/api/engagement-trends')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('engagementTrendChart').getContext('2d');
            
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
            gradient.addColorStop(1, 'rgba(118, 75, 162, 0.2)');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.weeks.map(w => `Week ${w}`),
                    datasets: [{
                        label: 'Average Engagement Score',
                        data: data.engagement,
                        backgroundColor: gradient,
                        borderColor: 'rgb(102, 126, 234)',
                        borderWidth: 4,
                        tension: 0.4,
                        fill: true,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: 'rgb(102, 126, 234)',
                        pointBorderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 3,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    return `Engagement: ${context.parsed.y.toFixed(2)}/10`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 10,
                            title: {
                                display: true,
                                text: 'Engagement Score',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading engagement trend:', error));
}

// Analytics Page Charts

function loadTrainingMetrics() {
    fetch('/api/training-metrics')
        .then(response => response.json())
        .then(data => {
            if (!data.model_metrics) {
                console.log('No training metrics available');
                return;
            }

            if (!data.training_history || !data.training_history.loss) {
                console.log('No training history available');
                return;
            }
            
            // Update metric displays
            document.getElementById('testLoss').textContent = data.model_metrics.loss.toFixed(4);
            document.getElementById('testMAE').textContent = data.model_metrics.mae.toFixed(4);
            document.getElementById('testRMSE').textContent = data.model_metrics.rmse.toFixed(4);
            document.getElementById('trainingDate').textContent = data.timestamp;
            
            const history = data.training_history;
            const epochs = history.loss.map((_, i) => i + 1);

            // Loss Chart
            const lossCtx = document.getElementById('lossChart').getContext('2d');
            new Chart(lossCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [{
                        label: 'Training Loss',
                        data: history.loss,
                        borderColor: 'rgb(52, 152, 219)',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        tension: 0.4,
                        borderWidth: 3
                    }, {
                        label: 'Validation Loss',
                        data: history.val_loss,
                        borderColor: 'rgb(231, 76, 60)',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4,
                        borderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: 'Training & Validation Loss',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Loss (MSE)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Epoch'
                            }
                        }
                    }
                }
            });
            
            // MAE Chart
            const maeCtx = document.getElementById('maeChart').getContext('2d');
            new Chart(maeCtx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [{
                        label: 'Training MAE',
                        data: history.mae,
                        borderColor: 'rgb(46, 204, 113)',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4,
                        borderWidth: 3
                    }, {
                        label: 'Validation MAE',
                        data: history.val_mae,
                        borderColor: 'rgb(243, 156, 18)',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        tension: 0.4,
                        borderWidth: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        title: {
                            display: true,
                            text: 'Mean Absolute Error',
                            font: { size: 14, weight: 'bold' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'MAE'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Epoch'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading training metrics:', error));
}

function loadWeeklyMetrics() {
    fetch('/api/engagement-trends')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('weeklyMetricsChart');
            if (!ctx) return;
            
            new Chart(ctx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.weeks.map(w => `Week ${w}`),
                    datasets: [{
                        label: 'Average Engagement',
                        data: data.engagement,
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgb(102, 126, 234)',
                        borderWidth: 2,
                        borderRadius: 8,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 3,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 10,
                            title: {
                                display: true,
                                text: 'Engagement Score',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading weekly metrics:', error));
}

function loadTimePerformanceChart() {
    fetch('/api/time-performance')
        .then(response => response.json())
        .then(data => {
            const canvas = document.getElementById('timePerformanceChart');
            if (!canvas) return;

            new Chart(canvas.getContext('2d'), {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Student Sessions',
                        data: data.points,
                        backgroundColor: 'rgba(52, 152, 219, 0.7)',
                        borderColor: 'rgb(52, 152, 219)',
                        borderWidth: 1,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    const x = context.parsed.x.toFixed(1);
                                    const y = context.parsed.y.toFixed(0);
                                    return `Time: ${x} hrs, Score: ${y}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Time Spent (Hours)',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Quiz Score',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading time vs performance chart:', error));
}

function loadEngagementDistribution() {
    fetch('/api/engagement-distribution')
        .then(response => response.json())
        .then(data => {
            const canvas = document.getElementById('engagementDistChart');
            if (!canvas) return;

            new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Students',
                        data: data.counts,
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgb(102, 126, 234)',
                        borderWidth: 2,
                        borderRadius: 6,
                        borderSkipped: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    return `Students: ${context.parsed.y}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Engagement Score Range',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            },
                            title: {
                                display: true,
                                text: 'Number of Students',
                                font: { weight: 'bold' }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading engagement distribution:', error));
}

// Predictions Page Charts

function loadRiskDistribution() {
    fetch('/api/risk-distribution')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('riskDistributionChart');
            if (!ctx) return;
            
            const riskColors = {
                'Low Risk': 'rgba(46, 204, 113, 0.8)',
                'Medium-Low Risk': 'rgba(52, 152, 219, 0.8)',
                'Medium Risk': 'rgba(243, 156, 18, 0.8)',
                'High Risk': 'rgba(231, 76, 60, 0.8)'
            };
            
            const colors = data.labels.map(label => riskColors[label] || 'rgba(149, 165, 166, 0.8)');
            
            new Chart(ctx.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: colors,
                        borderWidth: 3,
                        borderColor: '#fff',
                        hoverOffset: 15
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 1.5,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: { size: 12, weight: 'bold' }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 15,
                            cornerRadius: 8,
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} students (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading risk distribution:', error));
}

// Platform Distribution Chart
function loadPlatformChart() {
    fetch('/api/platform-distribution')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('platformChart').getContext('2d');
            
            // Colors for e-learning platforms
            const platformColors = {
                'Coursera': { bg: 'rgba(0, 123, 255, 0.8)', border: 'rgb(0, 123, 255)' },      // Blue
                'Udemy': { bg: 'rgba(236, 82, 164, 0.8)', border: 'rgb(236, 82, 164)' },       // Purple/Pink
                'Upgrad': { bg: 'rgba(255, 92, 0, 0.8)', border: 'rgb(255, 92, 0)' },          // Orange
                "Byju's": { bg: 'rgba(76, 175, 80, 0.8)', border: 'rgb(76, 175, 80)' },        // Green
                'Vedantu': { bg: 'rgba(255, 193, 7, 0.8)', border: 'rgb(255, 193, 7)' },       // Amber
                'Toppr': { bg: 'rgba(121, 85, 72, 0.8)', border: 'rgb(121, 85, 72)' },         // Brown
                'Simplilearn': { bg: 'rgba(3, 169, 244, 0.8)', border: 'rgb(3, 169, 244)' },   // Light Blue
                'SWAYAM': { bg: 'rgba(156, 39, 176, 0.8)', border: 'rgb(156, 39, 176)' },      // Purple
                'DIKSHA': { bg: 'rgba(0, 150, 136, 0.8)', border: 'rgb(0, 150, 136)' },        // Teal
                'NPTEL': { bg: 'rgba(63, 81, 181, 0.8)', border: 'rgb(63, 81, 181)' },         // Indigo
                'eSkill India': { bg: 'rgba(255, 87, 34, 0.8)', border: 'rgb(255, 87, 34)' },  // Deep Orange
                'Khan Academy': { bg: 'rgba(139, 195, 74, 0.8)', border: 'rgb(139, 195, 74)' } // Light Green
            };
            
            const backgrounds = data.labels.map(label => platformColors[label]?.bg || 'rgba(102, 126, 234, 0.8)');
            const borders = data.labels.map(label => platformColors[label]?.border || 'rgb(102, 126, 234)');
            
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: backgrounds,
                        borderColor: borders,
                        borderWidth: 2,
                        hoverOffset: 15
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 1.5,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                font: { size: 12, weight: 'bold' },
                                generateLabels: function(chart) {
                                    const data = chart.data;
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        return {
                                            text: `${label}: ${value} students`,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].borderColor[i],
                                            lineWidth: 2,
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 15,
                            cornerRadius: 8,
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${label}: ${value} students (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading platform distribution:', error));
}

// Course Distribution Chart
function loadCourseChart() {
    fetch('/api/course-distribution')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('courseChart').getContext('2d');
            
            // Color palette for courses
            const courseColors = [
                'rgba(102, 126, 234, 0.8)',  // Python - Purple
                'rgba(231, 76, 60, 0.8)',    // Data Science - Red
                'rgba(46, 204, 113, 0.8)',   // Machine Learning - Green
                'rgba(243, 156, 18, 0.8)',   // AI & Deep Learning - Orange
                'rgba(52, 152, 219, 0.8)'    // Web Development - Blue
            ];
            
            const courseBorders = [
                'rgb(102, 126, 234)',
                'rgb(231, 76, 60)',
                'rgb(46, 204, 113)',
                'rgb(243, 156, 18)',
                'rgb(52, 152, 219)'
            ];
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Students Enrolled',
                        data: data.values,
                        backgroundColor: courseColors.slice(0, data.labels.length),
                        borderColor: courseBorders.slice(0, data.labels.length),
                        borderWidth: 2,
                        borderRadius: 8,
                        hoverBackgroundColor: courseBorders.slice(0, data.labels.length)
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 1.5,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            padding: 15,
                            cornerRadius: 8,
                            titleFont: { size: 14, weight: 'bold' },
                            bodyFont: { size: 13 },
                            callbacks: {
                                label: function(context) {
                                    return `Students: ${context.parsed.y}`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                font: { weight: 'bold' }
                            },
                            title: {
                                display: true,
                                text: 'Number of Students',
                                font: { weight: 'bold', size: 12 }
                            },
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            }
                        },
                        x: {
                            ticks: {
                                font: { weight: 'bold' }
                            },
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading course distribution:', error));
}

// Student-to-Course Enrollment Mapping Chart
function loadStudentCourseMapChart() {
    const container = document.getElementById('studentCourseMapChart');
    if (!container) return;

    fetch('/api/student-course-map')
        .then(response => response.json())
        .then(data => {
            const courseLabels = data.courses || [];
            const points = data.points || [];

            const uniqueStudents = [...new Set(points.map(p => p.x))].sort((a, b) => a - b);
            if (uniqueStudents.length === 0 || courseLabels.length === 0) {
                container.innerHTML = '<div style="padding: 12px; color: #7f8c8d;">No student-course enrollment data available.</div>';
                return;
            }

            const enrollmentSet = new Set(points.map(p => `${p.x}||${p.course}`));
            const courseToStudentCount = {};
            points.forEach(p => {
                courseToStudentCount[p.course] = (courseToStudentCount[p.course] || 0) + 1;
            });

            const pageSize = 15;
            let currentPage = 1;
            let query = '';

            const style = `
                <style>
                    .scm-toolbar { display:flex; justify-content:space-between; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:10px; }
                    .scm-summary { display:flex; gap:16px; flex-wrap:wrap; font-size:12px; color:#475569; }
                    .scm-search { max-width:260px; }
                    .scm-grid-wrap { border:1px solid #e2e8f0; border-radius:12px; overflow:auto; background:#ffffff; }
                    .scm-table { border-collapse: separate; border-spacing: 0; min-width: 920px; width: 100%; font-size: 12px; }
                    .scm-table th, .scm-table td { border-bottom:1px solid #edf2f7; border-right:1px solid #edf2f7; padding:8px 10px; text-align:center; }
                    .scm-table th { background:#f8fafc; color:#0f172a; font-weight:700; white-space:nowrap; }
                    .scm-table th:first-child, .scm-table td:first-child { position: sticky; left:0; background:#f8fafc; z-index:1; text-align:left; font-weight:600; }
                    .scm-cell { width:28px; min-width:28px; }
                    .scm-on { background: linear-gradient(180deg, #4ade80, #16a34a); color:#ffffff; font-weight:700; }
                    .scm-off { background:#f8fafc; color:#cbd5e1; }
                    .scm-footer { display:flex; justify-content:space-between; align-items:center; margin-top:10px; gap:12px; flex-wrap:wrap; font-size:12px; color:#64748b; }
                    .scm-btn { border:1px solid #d1d5db; background:#fff; padding:4px 10px; border-radius:8px; cursor:pointer; }
                    .scm-btn:disabled { opacity:0.45; cursor:not-allowed; }
                </style>
            `;

            container.innerHTML = `
                ${style}
                <div class="scm-toolbar">
                    <div class="scm-summary">
                        <span><strong>${uniqueStudents.length}</strong> students</span>
                        <span><strong>${courseLabels.length}</strong> courses</span>
                        <span><strong>${points.length}</strong> enrollment links</span>
                    </div>
                    <input id="scmSearch" class="form-control form-control-sm scm-search" placeholder="Search student id..." />
                </div>
                <div id="scmGrid" class="scm-grid-wrap"></div>
                <div class="scm-footer">
                    <span id="scmPageInfo"></span>
                    <div>
                        <button id="scmPrev" class="scm-btn">Prev</button>
                        <button id="scmNext" class="scm-btn">Next</button>
                    </div>
                </div>
            `;

            const gridEl = container.querySelector('#scmGrid');
            const pageInfoEl = container.querySelector('#scmPageInfo');
            const prevBtn = container.querySelector('#scmPrev');
            const nextBtn = container.querySelector('#scmNext');
            const searchEl = container.querySelector('#scmSearch');

            function filteredStudents() {
                if (!query) return uniqueStudents;
                return uniqueStudents.filter(id => String(id).includes(query));
            }

            function renderMatrix() {
                const students = filteredStudents();
                const totalPages = Math.max(1, Math.ceil(students.length / pageSize));
                if (currentPage > totalPages) currentPage = totalPages;

                const start = (currentPage - 1) * pageSize;
                const pageStudents = students.slice(start, start + pageSize);

                const head = courseLabels.map(course => {
                    const count = courseToStudentCount[course] || 0;
                    return `<th title="${course}">${course} (${count})</th>`;
                }).join('');

                const rows = pageStudents.map(studentId => {
                    const cells = courseLabels.map(course => {
                        const on = enrollmentSet.has(`${studentId}||${course}`);
                        const klass = on ? 'scm-on' : 'scm-off';
                        const text = on ? '✓' : '•';
                        const tip = on
                            ? `Student ${studentId} enrolled in ${course}`
                            : `Student ${studentId} not enrolled in ${course}`;
                        return `<td class="scm-cell ${klass}" title="${tip}">${text}</td>`;
                    }).join('');
                    return `<tr><td>Student ${studentId}</td>${cells}</tr>`;
                }).join('');

                gridEl.innerHTML = `
                    <table class="scm-table">
                        <thead><tr><th>Student \\ Course</th>${head}</tr></thead>
                        <tbody>${rows || '<tr><td colspan="100%" style="text-align:center; padding:14px; color:#64748b;">No students match this search.</td></tr>'}</tbody>
                    </table>
                `;

                pageInfoEl.textContent = `Showing ${pageStudents.length} of ${students.length} students (Page ${currentPage}/${totalPages})`;
                prevBtn.disabled = currentPage <= 1;
                nextBtn.disabled = currentPage >= totalPages;
            }

            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage -= 1;
                    renderMatrix();
                }
            });

            nextBtn.addEventListener('click', () => {
                const totalPages = Math.max(1, Math.ceil(filteredStudents().length / pageSize));
                if (currentPage < totalPages) {
                    currentPage += 1;
                    renderMatrix();
                }
            });

            searchEl.addEventListener('input', () => {
                query = searchEl.value.trim();
                currentPage = 1;
                renderMatrix();
            });

            renderMatrix();
        })
        .catch(error => console.error('Error loading student-course map:', error));
}

// Utility Functions

function createGradient(ctx, color1, color2) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color1);
    gradient.addColorStop(1, color2);
    return gradient;
}

function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Chart error:', e.error);
});
