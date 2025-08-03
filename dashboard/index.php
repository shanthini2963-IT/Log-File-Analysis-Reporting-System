<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Log File Analysis Dashboard</title>
  <link rel="stylesheet" href="style.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>

  <div class="container">
    <h1>📊 Log File Analysis & Reporting Dashboard</h1>


    <div class="card">
      <label for="report-type"><strong>Select Report Type:</strong></label>
      <select id="report-type">
        <option value="top_ips">Top IPs</option>
        <option value="status_codes">Status Code Distribution</option>
        <option value="os_distribution">OS Distribution</option>
        <option value="hourly_traffic">Hourly Traffic</option>
        <option value="top_urls">Top Requested URLs</option>
      </select>
    </div>
    <div id="chart-container"></div>
  </div>

  <script src="main.js"></script>
</body>
</html>
