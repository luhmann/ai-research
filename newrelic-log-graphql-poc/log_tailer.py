#!/usr/bin/env python3
"""
Main log tailer application
Tails New Relic logs and replays them as GraphQL mutations
"""
import json
import time
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import sys

from newrelic_client import NewRelicClient
from log_processor import LogProcessor
from graphql_client import GraphQLClient, MutationMapper


class LogTailer:
    """Main application for tailing logs and replaying as GraphQL mutations"""

    def __init__(self, config_path: str):
        """
        Initialize log tailer

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.last_timestamp: Optional[int] = None
        self.processed_count = 0
        self.error_count = 0

        # Initialize clients
        nr_config = self.config["newrelic"]
        self.nr_client = NewRelicClient(
            api_key=nr_config["api_key"],
            account_id=nr_config["account_id"]
        )

        self.log_processor = LogProcessor(self.config)

        gql_config = self.config["graphql"]
        self.gql_client = GraphQLClient(endpoint=gql_config["endpoint"])
        self.mutation_mapper = MutationMapper(gql_config["mutation_template"])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)

    def fetch_new_logs(self) -> list[Dict[str, Any]]:
        """
        Fetch new logs from New Relic

        Returns:
            List of new log entries
        """
        base_query = self.config["newrelic"]["nrql_query"]

        # Remove any existing SINCE clause from base query
        if "SINCE" in base_query.upper():
            base_query = base_query.split("SINCE")[0].strip()

        logs = self.nr_client.tail_logs(base_query, self.last_timestamp)

        if logs:
            # Update last timestamp
            latest = self.nr_client.get_latest_timestamp(logs)
            if latest:
                self.last_timestamp = latest

        return logs

    def process_and_send(self, logs: list[Dict[str, Any]]) -> None:
        """
        Process logs and send as GraphQL mutations

        Args:
            logs: List of raw log entries
        """
        if not logs:
            return

        # Filter and extract data
        processed_logs = self.log_processor.process_logs(logs)

        if not processed_logs:
            print(f"  No logs matched filters (fetched {len(logs)} logs)")
            return

        print(f"  Processed {len(processed_logs)} logs (filtered from {len(logs)})")

        # Send as GraphQL mutations
        mutation = self.config["graphql"]["mutation_template"]
        results = self.gql_client.batch_execute(mutation, processed_logs)

        # Report results
        for result in results:
            if result["response"]["success"]:
                self.processed_count += 1
                print(f"  ✓ Mutation successful")
            else:
                self.error_count += 1
                print(f"  ✗ Mutation failed: {result['response'].get('error', 'Unknown error')}")

    def run(self, max_iterations: Optional[int] = None, verbose: bool = False) -> None:
        """
        Run the log tailer

        Args:
            max_iterations: Maximum number of iterations (None for infinite)
            verbose: Enable verbose output
        """
        poll_interval = self.config["newrelic"].get("poll_interval_seconds", 5)
        iteration = 0

        print("Starting New Relic Log Tailer")
        print(f"Polling interval: {poll_interval}s")
        print(f"GraphQL endpoint: {self.config['graphql']['endpoint']}")
        print("-" * 60)

        try:
            while max_iterations is None or iteration < max_iterations:
                iteration += 1
                print(f"\n[Iteration {iteration}] Fetching logs...")

                # Fetch new logs
                logs = self.fetch_new_logs()

                if verbose and logs:
                    print(f"  Raw logs fetched: {len(logs)}")
                    for i, log in enumerate(logs[:3]):  # Show first 3
                        print(f"    Log {i+1}: {json.dumps(log, indent=2)[:200]}...")

                # Process and send
                self.process_and_send(logs)

                # Stats
                print(f"  Stats: {self.processed_count} sent, {self.error_count} errors")

                # Wait before next poll
                if max_iterations is None or iteration < max_iterations:
                    time.sleep(poll_interval)

        except KeyboardInterrupt:
            print("\n\nStopping log tailer...")
        finally:
            print(f"\nFinal stats: {self.processed_count} mutations sent, {self.error_count} errors")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Tail New Relic logs and replay as GraphQL mutations"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "-n", "--iterations",
        type=int,
        default=None,
        help="Maximum number of iterations (default: infinite)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Check if config exists
    if not Path(args.config).exists():
        print(f"Error: Config file '{args.config}' not found")
        print("Please copy config.example.json to config.json and configure it")
        sys.exit(1)

    # Run tailer
    tailer = LogTailer(args.config)
    tailer.run(max_iterations=args.iterations, verbose=args.verbose)


if __name__ == "__main__":
    main()
