# 🔍 Log File Analysis & Reporting System

A command-line and web-based log file analyzer that parses Apache-style access logs, stores them in a MySQL database, and generates insightful reports via a PHP dashboard.

## 📁 Project Structure

```

Project-1 log analysis and report/
│
├── dashboard/                 # PHP dashboard with charts
│   ├── index.php             # Main dashboard page
│   ├── reports.php           # Backend API for chart data
│   ├── db.php                # Database connection handler
│   ├── style.css             # Styling for dashboard
│   └── main.js               # Chart logic and fetch
│
├── log\_analyzer\_cli/         # CLI-based log processor
│   ├── main.py               # Entry point for CLI
│   ├── log\_parser.py         # Log parsing logic
│   ├── mysql\_handler.py      # DB handler class
│   ├── config.ini            # DB and regex config
│   ├── generate\_realistic\_logs.py # Log generator
│   ├── requirements.txt      # Python dependencies
│   ├── sample\_logs/          # Sample access logs
│   └── sql/                  # SQL scripts

````

---

## 🚀 Features

- ✅ CLI for processing and inserting logs into MySQL
- ✅ Regex-based log parsing with user-agent analysis
- ✅ OS and device detection
- ✅ PHP + Chart.js web dashboard with:
  - Status Code Distribution
  - Hourly Traffic Report
  - OS Distribution
  - Top IP Addresses
  - Top Requested URLs

---

## 🐍 CLI Usage (Python)

```bash
# Process a log file
python main.py process_logs sample_logs/access.log

# Generate reports
python main.py generate_report status_code_distribution
python main.py generate_report hourly_traffic
python main.py generate_report os_distribution
python main.py generate_report top_n_ips 5
python main.py generate_report top_n_urls 5
````

---

## 🌐 Web Dashboard (PHP)

Start a PHP server inside the `dashboard/` directory:

```bash
cd dashboard
php -S localhost:8000
```

Then open `http://localhost:8000` in your browser.

> ⚠️ Make sure PHP and MySQL are installed and running.

---

## ⚙️ Configuration

Edit `config.ini` to update DB credentials or regex:

```ini
[mysql]
host = localhost
port = 3306
user = root
password = your_password
database = project1

[log]
regex = your_regex_here
```

---

## 📦 Dependencies

### Python

* `mysql-connector-python`
* `tabulate`
* `argparse`
* `re`, `logging`

Install with:

```bash
pip install -r requirements.txt
```

### PHP

* PHP 8+
* MySQLi or PDO enabled

---

## 🛠️ Author

**Your Name**
📧 \[shanthiniramanjaneya@gmail.com ]
🔗 \[(https://github.com/shanthini2963-IT)]

