import argparse
import logging
import configparser
from tabulate import tabulate
from log_parser import LogParser
from mysql_handler import MySQLHandler
from datetime import datetime


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CLIManager:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.parser = argparse.ArgumentParser(description="Web Server Log Analyzer CLI")
        self._add_subcommands()

    def _add_subcommands(self):
        subparsers = self.parser.add_subparsers(dest='command', help='Main commands')

    # Command to process logs
        process_parser = subparsers.add_parser('process_logs', help='Load logs from a file')
        process_parser.add_argument('file_path', type=str, help='Path to log file')
        process_parser.add_argument('--batch_size', type=int, default=1000, help='Insert batch size')

    # Command to generate reports
        report_parser = subparsers.add_parser('generate_report', help='Generate reports')
        report_subs = report_parser.add_subparsers(dest='report_type', help='Report types')

        report_subs.add_parser('status_code_distribution', help='Show status code breakdown')
        report_subs.add_parser('hourly_traffic', help='Show hourly traffic volume')
        report_subs.add_parser('os_distribution', help='Show OS traffic breakdown')

        top_ips = report_subs.add_parser('top_n_ips', help='Top IPs by request count')
        top_ips.add_argument('n', type=int, help='Number of IPs to show')

        top_urls = report_subs.add_parser('top_n_urls', help='Top requested URLs')
        top_urls.add_argument('n', type=int, help='Number of URLs to show')

        error_logs = report_subs.add_parser('error_logs', help='Logs for specific HTTP error code')
        error_logs.add_argument('status_code', type=int, help='Error status code (e.g., 404)')

    # ✅ New: Error logs filtered by specific date
        error_logs_by_date = report_subs.add_parser('error_logs_by_date', help='Logs for all errors on a specific date')
        error_logs_by_date.add_argument('date', type=str, help='Date in YYYY-MM-DD format')
        
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
        batch, total = [], 0

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parsed = log_parser.parse_line(line)
                    if parsed:
                        batch.append(parsed)
                        if len(batch) >= batch_size:
                            self.db_handler.insert_batch_log_entries(batch)
                            total += len(batch)
                            batch = []
                if batch:
                    self.db_handler.insert_batch_log_entries(batch)
                    total += len(batch)
            logging.info(f"Finished processing log file. Total lines loaded: {total}")
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except Exception as e:
            logging.error(f"Error while processing logs: {e}")

    def _generate_report(self, args):
        fetch = self.db_handler

        report_map = {
            'status_code_distribution': lambda: fetch.get_status_code_distribution(),
            'hourly_traffic': lambda: fetch.get_hourly_traffic(),
            'os_distribution': lambda: fetch.get_os_distribution(),
            'top_n_ips': lambda: fetch.get_top_n_ips(args.n),
            'top_n_urls': lambda: fetch.get_top_n_requested_urls(args.n),
            'error_logs': lambda: fetch.get_error_logs(args.status_code),
            'error_logs_by_date': lambda: fetch.get_error_logs_by_date(args.date)
        }

        if args.report_type not in report_map:
            logging.warning("Invalid report type specified.")
            return

        results = report_map[args.report_type]()
        if results:
            print(tabulate(results, headers="keys", tablefmt="grid"))
        else:
            print("No data available for this report.")


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    db_cfg = config['mysql']
    db_handler = MySQLHandler(**db_cfg)
    db_handler.create_tables()

    cli = CLIManager(db_handler)
    cli.run()

    db_handler.close()


if __name__ == "__main__":
    main()
