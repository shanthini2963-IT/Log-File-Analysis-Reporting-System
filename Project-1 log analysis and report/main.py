# main.py

import argparse
import logging
import configparser
from tabulate import tabulate
from log_parser import LogParser
from mysql_handler import MySQLHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CLIManager:
    """Manages the command-line interface."""
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.parser = argparse.ArgumentParser(description="Web Server Log Analyzer & Reporting CLI")
        self._setup_parser()

    def _setup_parser(self):
        subparsers = self.parser.add_subparsers(dest='command', help='Available commands')

        # Process logs
        process_parser = subparsers.add_parser('process_logs', help='Parse and load logs from a file')
        process_parser.add_argument('file_path', type=str, help='Path to the log file')
        process_parser.add_argument('--batch_size', type=int, default=1000, help='Batch size for DB inserts')

        # Report command
        report_parser = subparsers.add_parser('generate_report', help='Generate analytical reports')
        report_subparsers = report_parser.add_subparsers(dest='report_type', help='Types of reports')

        top_ips_parser = report_subparsers.add_parser('top_n_ips', help='Top N requesting IP addresses')
        top_ips_parser.add_argument('n', type=int, default=10, help='Number of top IPs')

        status_code_parser = report_subparsers.add_parser('status_code_distribution', help='HTTP status code breakdown')

    def run(self):
        args = self.parser.parse_args()

        if args.command == 'process_logs':
            self._process_logs(args.file_path, args.batch_size)
        elif args.command == 'generate_report':
            self._generate_report(args)
        else:
            self.parser.print_help()

    def _process_logs(self, file_path, batch_size):
        log_parser = LogParser()
        processed_count = 0
        batch = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parsed = log_parser.parse_line(line)
                    if parsed:
                        batch.append(parsed)
                        if len(batch) >= batch_size:
                            self.db_handler.insert_batch_log_entries(batch)
                            processed_count += len(batch)
                            batch = []
                if batch:
                    self.db_handler.insert_batch_log_entries(batch)
                    processed_count += len(batch)
            logging.info(f"Finished processing log file. Total lines loaded: {processed_count}")
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except Exception as e:
            logging.error(f"Error during log processing: {e}")

    def _generate_report(self, args):
        if args.report_type == 'top_n_ips':
            results = self.db_handler.get_top_n_ips(args.n)
            print(tabulate(results, headers=["IP Address", "Request Count"], tablefmt="grid"))

        elif args.report_type == 'status_code_distribution':
            results = self.db_handler.get_status_code_distribution()
            print(tabulate(results, headers=["Status Code", "Count", "Percentage"], tablefmt="grid"))

        else:
            logging.warning("Invalid report type.")
            self.parser.print_help()


def main():
    # Load config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    db_config = {
        'host': config['mysql']['host'],
        'user': config['mysql']['user'],
        'password': config['mysql']['password'],
        'database': config['mysql']['database']
    }

    db_handler = MySQLHandler(**db_config)
    db_handler.create_tables()

    cli_manager = CLIManager(db_handler)
    cli_manager.run()

    db_handler.close()

if __name__ == "__main__":
    main()
