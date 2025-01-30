// Update this when deploying
const BASE_URL = window.location.origin;
let errorCodesChart, connectionTypesChart, timelineChart;
let errorTable;
let ENDPOINT_PATH;

document.addEventListener('DOMContentLoaded', function() {
    // Fetch configuration from server
    fetch(`${BASE_URL}/config`)
        .then(r => r.json())
        .then(config => {
            ENDPOINT_PATH = config.ENDPOINT_PATH;
            // Display webhook URL
            const webhookUrl = `${BASE_URL}${ENDPOINT_PATH}`;
            document.getElementById('webhook-url').textContent = webhookUrl;
        });
    
    initializeDataTable();
    initializeCharts();
    fetchLogsAndStats();
    setInterval(fetchLogsAndStats, 5000);  // Refresh every 5 seconds

    // Add event listener for severity filter
    document.getElementById('severityFilter').addEventListener('change', function() {
        errorTable.draw();
    });
});

function initializeDataTable() {
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex) {
        const severity = data[1]; // Severity is in the second column
        const filterValue = document.getElementById('severityFilter').value;
        return filterValue === 'all' || severity.toLowerCase() === filterValue;
    });

    errorTable = $('#errorTable').DataTable({
        responsive: true,
        order: [[0, 'desc']], // Sort by timestamp descending
        pageLength: 10,
        columns: [
            { 
                data: 'timestamp',
                render: function(data) {
                    return formatTimestamp(data);
                }
            },
            { 
                data: 'severity',
                render: function(data) {
                    return `<span class="severity-${data.toLowerCase()}">${data}</span>`;
                }
            },
            { data: 'errorCode' },
            { data: 'connectionType' },
            { data: 'errorMessage' },
            { 
                data: 'additionalInfo',
                render: function(data) {
                    return `
                        <div class="additional-info">
                            <div><strong>Type:</strong> ${data.type}</div>
                            <div><strong>Consumer ID:</strong> ${data.consumer_id}</div>
                            <div><strong>Account ID:</strong> ${data.account_id}</div>
                            <div><strong>Customer ID:</strong> ${data.customer_id}</div>
                        </div>
                    `;
                }
            }
        ],
        columnDefs: [
            {
                targets: 5,
                className: 'none' // This column will be hidden by default but expandable
            }
        ]
    });
}

function initializeCharts() {
    // Error Codes Chart
    errorCodesChart = new Chart(document.getElementById('errorCodesChart'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Error Codes',
                data: [],
                backgroundColor: '#4a90e2',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: false
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

    // Connection Types Chart
    connectionTypesChart = new Chart(document.getElementById('connectionTypesChart'), {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#4a90e2', '#50e3c2', '#f5a623', '#e54d42', '#b8e986'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            },
            cutout: '60%'
        }
    });

    // Timeline Chart
    timelineChart = new Chart(document.getElementById('timelineChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Errors',
                data: [],
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
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
}

function updateCharts(stats) {
    // Update Error Codes Chart
    errorCodesChart.data.labels = Object.keys(stats.error_codes);
    errorCodesChart.data.datasets[0].data = Object.values(stats.error_codes);
    errorCodesChart.update();

    // Update Connection Types Chart
    connectionTypesChart.data.labels = Object.keys(stats.connection_types);
    connectionTypesChart.data.datasets[0].data = Object.values(stats.connection_types);
    connectionTypesChart.update();

    // Update Timeline Chart
    const sortedHours = Object.keys(stats.hourly_errors).sort();
    timelineChart.data.labels = sortedHours;
    timelineChart.data.datasets[0].data = sortedHours.map(hour => stats.hourly_errors[hour]);
    timelineChart.update();
}

function fetchLogsAndStats() {
    Promise.all([
        fetch(`${BASE_URL}/logs`).then(r => r.json()),
        fetch(`${BASE_URL}/stats`).then(r => r.json())
    ]).then(([logs, stats]) => {
        updateStats(logs);
        updateCharts(stats);
        updateTable(logs);
    }).catch(error => console.error('Error fetching data:', error));
}

function copyWebhookUrl() {
    const webhookUrl = document.getElementById('webhook-url').textContent;
    navigator.clipboard.writeText(webhookUrl).then(() => {
        alert('Webhook URL copied to clipboard!');
    });
}

function updateStats(logs) {
    const totalErrors = logs.length;
    const criticalErrors = logs.filter(log => log.severity === 'critical').length;
    const warningErrors = logs.filter(log => log.severity === 'warning').length;

    document.getElementById('total-errors').textContent = totalErrors;
    document.getElementById('critical-errors').textContent = criticalErrors;
    document.getElementById('warning-errors').textContent = warningErrors;
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function updateTable(logs) {
    errorTable.clear();
    errorTable.rows.add(logs);
    errorTable.draw();
}

function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        errorTable.clear().draw();
    }
} 