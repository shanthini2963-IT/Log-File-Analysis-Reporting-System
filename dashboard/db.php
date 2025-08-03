<?php
function getDbConnection() {
    // Read database configuration from config.ini
    $config = parse_ini_file("config.ini", true);

    if (!$config || !isset($config['mysql'])) {
        die("❌ Failed to read config.ini or [mysql] section missing.");
    }

    $dbConfig = $config['mysql'];
    $host = $dbConfig['host'] ?? 'localhost';
    $user = $dbConfig['user'] ?? '';
    $password = $dbConfig['password'] ?? '';
    $database = $dbConfig['database'] ?? '';

    // Create MySQL connection
    $conn = new mysqli($host, $user, $password, $database);

    // Check connection
    if ($conn->connect_error) {
        die("❌ Connection failed: " . $conn->connect_error);
    }

    return $conn;
}
?>
