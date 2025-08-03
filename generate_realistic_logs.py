from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
LOG_FILE_PATH = "sample_logs/access.log"
NUM_ENTRIES = 40000

# Status code distribution
status_pool = (
    [200] * 11200 +
    [404] * 4600 +
    [403] * 2200 +
    [500] * 1600 +
    [302] * 400
)

# Generate list of dates from 25 July to 2 Aug 2025
date_range = [datetime(2025, 7, 25) + timedelta(days=i) for i in range(9)]

# Sample HTTP methods and paths
methods = ['GET', 'POST', 'PUT', 'DELETE']
paths = ['/index.html', '/products', '/about', '/contact', '/login', '/dashboard', '/api/data', '/assets/logo.png']
http_versions = ['HTTP/1.1', 'HTTP/2']
referrers = [
    fake.uri(),
    '-',
    'http://example.com',
    'http://google.com',
    'http://klein.com/explore/list/categoryfaq.html'
]
user_agents = [
    fake.user_agent(),
    "Mozilla/5.0 (Linux; Android 10; SM-A107F)",
    "Chrome/91.0.4472.124 (Macintosh; Intel Mac OS X 10_15_7)",
    "Safari/537.36 (iPhone; CPU iPhone OS 14_2 like Mac OS X)",
    "PostmanRuntime/7.28.0",
    "curl/7.64.1"
]

def sanitize(s):
    """Ensure no double quotes that break log format."""
    return s.replace('"', '').replace('\n', '').strip()

def generate_log_entry():
    ip = fake.ipv4()
    date = random.choice(date_range)
    random_date = datetime(2025, 7, 25) + timedelta(days=random.randint(0, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    timestamp_str = random_date.strftime('%d/%b/%Y:%H:%M:%S +0000')
    method = random.choice(methods)
    path = random.choice(paths)
    version = random.choice(http_versions)
    status = random.choice(status_pool)
    size = random.randint(500, 5000)
    referer = sanitize(random.choice(referrers))
    user_agent = sanitize(random.choice(user_agents))

    return f'{ip} - - [{timestamp_str}] "{method} {path} {version}" {status} {size} "{referer}" "{user_agent}"\n'

# Write logs to file
with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
    for _ in range(NUM_ENTRIES):
        f.write(generate_log_entry())

print(f"✅ Generated {NUM_ENTRIES} clean log entries in {LOG_FILE_PATH}")

