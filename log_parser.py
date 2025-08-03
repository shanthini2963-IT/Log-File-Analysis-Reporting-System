# log_parser.py

import re
from datetime import datetime
import logging
import configparser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LogParser:
    """Parses individual log lines using regex."""

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            pattern = config['log']['regex']
            self.LOG_PATTERN = re.compile(pattern)
            logging.info("Loaded log pattern from config.ini")
        except KeyError:
            # Use default Apache Combined Log Format if regex not found in config
            logging.info("Using default Apache regex pattern.")
            self.LOG_PATTERN = re.compile(
                r'(?P<ip_address>\d{1,3}(?:\.\d{1,3}){3}) - - '
                r'\[(?P<timestamp>[^\]]+)\] '
                r'"(?P<method>[A-Z]+) (?P<path>\S+) HTTP/\d(?:\.\d+)?\" '
                r'(?P<status_code>\d{3}) (?P<bytes_sent>\d+|-) '
                r'"(?P<referrer>[^"]*)" '
                r'"(?P<user_agent>.*)"'
            )

    def parse_line(self, log_line):
        """Parses a single log line into structured data."""
        match = self.LOG_PATTERN.match(log_line)
        if match:
            try:
                timestamp_str = match.group("timestamp")

                # Try parsing with timezone first, fallback without
                try:
                    timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
                except ValueError:
                    timestamp = datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S')

                bytes_sent_str = match.group("bytes_sent")
                bytes_sent = int(bytes_sent_str) if bytes_sent_str != '-' else 0

                return {
                    "ip_address": match.group("ip_address"),
                    "timestamp": timestamp,
                    "method": match.group("method"),
                    "path": match.group("path"),
                    "status_code": int(match.group("status_code")),
                    "bytes_sent": bytes_sent,
                    "referrer": match.group("referrer") or None,
                    "user_agent": match.group("user_agent") or None,
                }

            except Exception as e:
                logging.warning(f"Failed to parse line due to error: {e}")
                return None
        else:
            logging.warning(f"Malformed log line skipped: {log_line.strip()}")
            return None