"""
Log processor for filtering and extracting data from log entries
"""
import re
import json
from typing import Dict, List, Any, Optional


class LogProcessor:
    """Process and filter log entries"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize log processor

        Args:
            config: Configuration dictionary with filters and mapping rules
        """
        self.filters = config.get("filters", {})
        self.mapping = config.get("mapping", {})

        # Compile regex patterns
        message_pattern = self.filters.get("message_pattern", ".*")
        self.message_regex = re.compile(message_pattern)

        self.required_fields = self.filters.get("required_fields", [])

    def filter_log(self, log: Dict[str, Any]) -> bool:
        """
        Check if a log entry matches filter criteria

        Args:
            log: Log entry dictionary

        Returns:
            True if log passes all filters, False otherwise
        """
        # Check required fields
        for field in self.required_fields:
            if field not in log or log[field] is None:
                return False

        # Check message pattern
        message = log.get("message", "")
        if isinstance(message, str) and not self.message_regex.match(message):
            return False

        return True

    def extract_data(self, log: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and map data from log entry according to mapping rules

        Args:
            log: Log entry dictionary

        Returns:
            Extracted data dictionary
        """
        extracted = {}

        for target_field, source_path in self.mapping.items():
            value = self._get_nested_value(log, source_path)
            if value is not None:
                extracted[target_field] = value

        return extracted

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get nested value from dictionary using dot notation

        Args:
            data: Source dictionary
            path: Dot-separated path (e.g., "data.user.name")

        Returns:
            Value at path, or None if not found
        """
        # Handle direct field access (no dots)
        if '.' not in path:
            return data.get(path)

        # Handle nested access
        keys = path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
                if current is None:
                    return None
            else:
                return None

        return current

    def process_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of logs: filter and extract data

        Args:
            logs: List of log entries

        Returns:
            List of processed/extracted data dictionaries
        """
        processed = []

        for log in logs:
            if self.filter_log(log):
                extracted = self.extract_data(log)
                if extracted:  # Only include if we extracted some data
                    # Include original log for debugging
                    extracted['_original_log'] = log
                    processed.append(extracted)

        return processed

    def extract_with_regex(self, log: Dict[str, Any], patterns: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using regex patterns on log message

        Args:
            log: Log entry
            patterns: Dictionary of field_name -> regex_pattern

        Returns:
            Dictionary of extracted values
        """
        extracted = {}
        message = str(log.get("message", ""))

        for field_name, pattern in patterns.items():
            match = re.search(pattern, message)
            if match:
                # Use named group if available, otherwise first group
                if match.lastindex and match.lastindex > 0:
                    extracted[field_name] = match.group(1)
                elif match.groupdict():
                    extracted[field_name] = match.groupdict().get(field_name)

        return extracted
