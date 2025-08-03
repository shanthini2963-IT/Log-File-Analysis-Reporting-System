<?php
header('Content-Type: application/json');

// Read config.ini
$config = parse_ini_file("config.ini", true);
$db = $config['mysql'];

// DB credentials
$host = $db['host'];
$user = $db['user'];
$password = $db['password'];
$database = $db['database'];

// Connect to MySQL
require_once 'db.php';
$conn = getDbConnection();

// Get report type from query string
$report = $_GET['report'] ?? null;
$data = [];

switch ($report) {
    case 'top_ips':
        $sql = "SELECT ip_address, COUNT(*) AS request_count
                FROM log_entries
                GROUP BY ip_address
                ORDER BY request_count DESC
                LIMIT 10";
        break;

    case 'status_codes':
        $sql = "SELECT status_code, COUNT(*) AS count
                FROM log_entries
                GROUP BY status_code
                ORDER BY count DESC";
        break;

    case 'os_distribution':
        $sql = "SELECT ua.os, COUNT(*) AS count
                FROM log_entries le
                JOIN user_agents ua ON le.user_agent_id = ua.id
                GROUP BY ua.os";
        break;

    case 'hourly_traffic':
        $sql = "SELECT HOUR(timestamp) AS hour, COUNT(*) AS count
                FROM log_entries
                GROUP BY hour
                ORDER BY hour";
        break;

    case 'top_urls':
        $sql = "SELECT path, COUNT(*) AS count
                FROM log_entries
                GROUP BY path
                ORDER BY count DESC
                LIMIT 10";
        break;

    default:
        http_response_code(400);
        echo json_encode(['error' => 'Invalid report type']);
        $conn->close();
        exit();
}

// Execute and return query
$result = $conn->query($sql);
if ($result) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
    echo json_encode($data);
} else {
    http_response_code(500);
    echo json_encode(['error' => 'Query failed']);
}

$conn->close();
?>
