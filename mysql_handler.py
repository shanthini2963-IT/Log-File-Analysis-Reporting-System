# mysql_handler.py

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MySQLHandler:
    """Handles MySQL connection, insertion, and reporting."""

    def __init__(self, host, user, password, database):
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
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

    def _get_or_insert_user_agent(self, user_agent):
        """Returns user_agent ID; inserts if new."""
        if not user_agent:
            return None

        try:
            self.cursor.execute(
                "SELECT id FROM user_agents WHERE user_agent_string = %s",
                (user_agent,)
            )
            result = self.cursor.fetchone()
            if result:
                return result['id']
            else:
                self.cursor.execute(
                    "INSERT INTO user_agents (user_agent_string) VALUES (%s)",
                    (user_agent,)
                )
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
        """Returns top N IP addresses by request count."""
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
        cursor = self.conn.cursor()
        cursor.execute(query, (n,))
        results = cursor.fetchall()
        cursor.close()
        return results


    def get_os_distribution(self):
        query = """
            SELECT ua.os, COUNT(*) AS requests
            FROM log_entries le
            JOIN user_agents ua ON le.user_agent_id = ua.id
            GROUP BY ua.os
            ORDER BY requests DESC;
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_error_logs(self, status_code):
        query = """
            SELECT ip_address, path, status_code, timestamp
            FROM log_entries
            WHERE status_code = %s
            ORDER BY timestamp DESC
            LIMIT 100;
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (status_code,))
        results = cursor.fetchall()
        cursor.close()
        return results
    

    def get_hourly_traffic(self):
        query = """
            SELECT HOUR(timestamp) AS hour, COUNT(*) AS request_count
            FROM log_entries
            GROUP BY hour
            ORDER BY hour;
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        return results



    def get_status_code_distribution(self):
        """Returns HTTP status code distribution and percentage."""
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

    def close(self):
        """Closes the DB connection."""
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            logging.info("MySQL connection closed.")
