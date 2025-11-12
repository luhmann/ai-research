"""
New Relic client for querying logs via NerdGraph API
"""
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class NewRelicClient:
    """Client for querying New Relic logs via NerdGraph GraphQL API"""

    NERDGRAPH_URL = "https://api.newrelic.com/graphql"

    def __init__(self, api_key: str, account_id: str):
        """
        Initialize New Relic client

        Args:
            api_key: New Relic User API Key
            account_id: New Relic Account ID
        """
        self.api_key = api_key
        self.account_id = account_id
        self.headers = {
            "Content-Type": "application/json",
            "API-Key": api_key
        }

    def query_logs(self, nrql_query: str, timeout: int = 10) -> List[Dict[str, Any]]:
        """
        Query logs using NRQL

        Args:
            nrql_query: NRQL query string (e.g., "SELECT * FROM Log SINCE 1 minute ago")
            timeout: Query timeout in seconds

        Returns:
            List of log entries as dictionaries
        """
        graphql_query = """
        query($accountId: Int!, $nrqlQuery: Nrql!) {
          actor {
            account(id: $accountId) {
              nrql(query: $nrqlQuery, timeout: %d) {
                results
              }
            }
          }
        }
        """ % timeout

        variables = {
            "accountId": int(self.account_id),
            "nrqlQuery": nrql_query
        }

        payload = {
            "query": graphql_query,
            "variables": variables
        }

        try:
            response = requests.post(
                self.NERDGRAPH_URL,
                headers=self.headers,
                json=payload,
                timeout=timeout + 5  # Add buffer to HTTP timeout
            )
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                print(f"GraphQL errors: {data['errors']}")
                return []

            # Extract results
            results = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
            return results

        except requests.exceptions.RequestException as e:
            print(f"Error querying New Relic: {e}")
            return []

    def tail_logs(self, base_query: str, since_timestamp: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Tail logs since a specific timestamp

        Args:
            base_query: Base NRQL query (without SINCE clause)
            since_timestamp: Unix timestamp in milliseconds. If None, queries last minute

        Returns:
            List of new log entries
        """
        if since_timestamp:
            # Query logs since the last timestamp
            # New Relic uses milliseconds for timestamps
            query = f"{base_query} SINCE {since_timestamp}"
        else:
            # Initial query - get logs from last minute
            query = f"{base_query} SINCE 1 minute ago"

        return self.query_logs(query)

    def get_latest_timestamp(self, logs: List[Dict[str, Any]]) -> Optional[int]:
        """
        Extract the latest timestamp from a list of logs

        Args:
            logs: List of log entries

        Returns:
            Latest timestamp in milliseconds, or None if no logs
        """
        if not logs:
            return None

        timestamps = []
        for log in logs:
            # Try different timestamp field names
            for field in ['timestamp', 'Timestamp', 'eventTime', 'logTimestamp']:
                if field in log and log[field]:
                    try:
                        # Handle both millisecond and second timestamps
                        ts = int(log[field])
                        # If timestamp is in seconds (< year 3000), convert to milliseconds
                        if ts < 32503680000:
                            ts = ts * 1000
                        timestamps.append(ts)
                        break
                    except (ValueError, TypeError):
                        continue

        return max(timestamps) if timestamps else None
