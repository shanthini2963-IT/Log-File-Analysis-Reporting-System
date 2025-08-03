document.addEventListener('DOMContentLoaded', () => {
    const reportSelector = document.getElementById('report-type');
    const chartContainer = document.getElementById('chart-container');

    // Load initial report
    fetchReport(reportSelector.value);

    reportSelector.addEventListener('change', () => {
        fetchReport(reportSelector.value);
    });

    function fetchReport(reportType) {
        fetch(`reports.php?report=${reportType}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Failed to load report.");
                }
                return response.json();
            })
            .then(data => {
                renderReport(data, reportType);
            })
            .catch(err => {
                chartContainer.innerHTML = `<p style="color:red;">${err.message}</p>`;
            });
    }

    function renderReport(data, reportType) {
        chartContainer.innerHTML = ''; // Clear previous chart

        if (!data || data.length === 0) {
            chartContainer.innerHTML = "<p>No data available.</p>";
            return;
        }

        const canvas = document.createElement('canvas');
        canvas.id = "reportChart";
        chartContainer.appendChild(canvas);

        let labels = [];
        let values = [];
        let title = '';

        switch (reportType) {
            case 'status_codes':
                labels = data.map(item => item.status_code);
                values = data.map(item => item.count);
                title = 'HTTP Status Code Distribution';
                break;

            case 'hourly_traffic':
                labels = data.map(item => item.hour);
                values = data.map(item => item.count);
                title = 'Hourly Traffic';
                break;

            case 'os_distribution':
                labels = data.map(item => item.os || "Unknown");
                values = data.map(item => item.count);
                title = 'OS Distribution';
                break;

            case 'top_ips':
                labels = data.map(item => item.ip_address);
                values = data.map(item => item.request_count);
                title = 'Top IPs by Requests';
                break;

            case 'top_urls':
                labels = data.map(item => item.path);
                values = data.map(item => item.count);
                title = 'Top Requested URLs';
                break;

            default:
                chartContainer.innerHTML = "<p>Unsupported report type.</p>";
                return;
        }

        new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: title,
                    data: values,
                    backgroundColor: 'rgba(52, 152, 219, 0.6)',
                    borderColor: 'rgba(41, 128, 185, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: title
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        ticks: {
                            autoSkip: false,
                            maxRotation: 45,
                            minRotation: 30
                        }
                    }
                }
            }
        });
    }
});
