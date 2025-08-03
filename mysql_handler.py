import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging
from user_agents import parse as parse_ua

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MySQLHandler:
    """Handles MySQL connection, insertion, and reporting."""

    def __init__(self, host, user, password, database, port):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            self.cursor = self.conn.cursor(dictionary=True)
            logging.info("Connected to MySQL database.")
        except Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def create_tables(self):
        """Creates user_agents and log_entries tables if they don't exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_agents (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_agent_string TEXT UNIQUE,
                    os VARCHAR(100),
                    browser VARCHAR(100),
                    device_type VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_entries (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip_address VARCHAR(45),
                    timestamp DATETIME,
                    method VARCHAR(10),
                    path TEXT,
                    status_code INT,
                    bytes_sent INT,
                    referrer TEXT,
                    user_agent_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_agent_id) REFERENCES user_agents(id)
                )
            """)
            self.conn.commit()
            logging.info("Tables ensured.")
        except Error as e:
            logging.error(f"Error creating tables: {e}")
            raise

    def _get_or_insert_user_agent(self, user_agent_str):
        """Returns user_agent ID; inserts if new with parsed OS, browser, device."""
        if not user_agent_str:
            return None

        try:
            self.cursor.execute(
                "SELECT id FROM user_agents WHERE user_agent_string = %s",
                (user_agent_str,)
            )
            result = self.cursor.fetchone()
            if result:
                return result['id']
            else:
                parsed_ua = parse_ua(user_agent_str)
                os = parsed_ua.os.family
                browser = parsed_ua.browser.family
                device_type = "Mobile" if parsed_ua.is_mobile else \
                              "Tablet" if parsed_ua.is_tablet else \
                              "PC" if parsed_ua.is_pc else \
                              "Bot" if parsed_ua.is_bot else "Other"

                self.cursor.execute("""
                    INSERT INTO user_agents (user_agent_string, os, browser, device_type)
                    VALUES (%s, %s, %s, %s)
                """, (user_agent_str, os, browser, device_type))
                self.conn.commit()
                return self.cursor.lastrowid
        except Error as e:
            logging.error(f"User agent insertion failed: {e}")
            return None

    def insert_batch_log_entries(self, log_data_list):
        """Insert a batch of parsed log entries."""
        try:
            entries_to_insert = []
            user_agent_cache = {}

            for entry in log_data_list:
                ua = entry['user_agent']
                if ua not in user_agent_cache:
                    user_agent_cache[ua] = self._get_or_insert_user_agent(ua)
                user_agent_id = user_agent_cache[ua]

                entries_to_insert.append((
                    entry['ip_address'],
                    entry['timestamp'],
                    entry['method'],
                    entry['path'],
                    entry['status_code'],
                    entry['bytes_sent'],
                    entry['referrer'],
                    user_agent_id
                ))

            insert_query = """
                INSERT INTO log_entries (
                    ip_address, timestamp, method, path, status_code,
                    bytes_sent, referrer, user_agent_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            self.cursor.executemany(insert_query, entries_to_insert)
            self.conn.commit()
            logging.info(f"Inserted {len(entries_to_insert)} log entries.")
        except Error as e:
            logging.error(f"Batch insert failed: {e}")

    def get_top_n_ips(self, n):
        try:
            self.cursor.execute("""
                SELECT ip_address, COUNT(*) AS request_count
                FROM log_entries
                GROUP BY ip_address
                ORDER BY request_count DESC
                LIMIT %s
            """, (n,))
            return [(row['ip_address'], row['request_count']) for row in self.cursor.fetchall()]
        except Error as e:
            logging.error(f"Failed to fetch top IPs: {e}")
            return []

    def get_top_n_requested_urls(self, n):
        query = """
            SELECT path, COUNT(*) AS request_count
            FROM log_entries
            GROUP BY path
            ORDER BY request_count DESC
            LIMIT %s;
        """
        self.cursor.execute(query, (n,))
        return self.cursor.fetchall()

    def get_os_distribution(self):
        query = """
            SELECT os, COUNT(*) AS requests
            FROM user_agents ua
            JOIN log_entries le ON le.user_agent_id = ua.id
            GROUP BY os
            ORDER BY requests DESC;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_error_logs(self, status_code):
        query = """
            SELECT ip_address, path, status_code, timestamp
            FROM log_entries
            WHERE status_code = %s
            ORDER BY timestamp DESC
            LIMIT 100;
        """
        self.cursor.execute(query, (status_code,))
        return self.cursor.fetchall()

    def get_hourly_traffic(self):
        query = """
            SELECT HOUR(timestamp) AS hour, COUNT(*) AS request_count
            FROM log_entries
            GROUP BY hour
            ORDER BY hour;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_status_code_distribution(self):
        try:
            self.cursor.execute("SELECT COUNT(*) as total FROM log_entries")
            total = self.cursor.fetchone()['total']

            self.cursor.execute("""
                SELECT status_code, COUNT(*) as count
                FROM log_entries
                GROUP BY status_code
                ORDER BY count DESC
            """)
            result = self.cursor.fetchall()
            return [
                (row['status_code'], row['count'], f"{(row['count'] / total * 100):.2f}%")
                for row in result
            ]
        except Error as e:
            logging.error(f"Failed to fetch status distribution: {e}")
            return []
        
    def get_error_logs_by_date(self, date_str):
        query = """
            SELECT ip_address, path, status_code, timestamp
            FROM log_entries
            WHERE DATE(timestamp) = %s AND status_code >= 400
            ORDER BY timestamp DESC
        """
        self.cursor.execute(query, (date_str,))
        return self.cursor.fetchall()


    def close(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            logging.info("MySQL connection closed.")
