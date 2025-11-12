"""
GraphQL client for sending mutations to local backend
"""
import requests
import json
from typing import Dict, Any, Optional


class GraphQLClient:
    """Client for executing GraphQL mutations"""

    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize GraphQL client

        Args:
            endpoint: GraphQL endpoint URL
            headers: Optional HTTP headers
        """
        self.endpoint = endpoint
        self.headers = headers or {}
        self.headers.setdefault("Content-Type", "application/json")

    def execute_mutation(self, mutation: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a GraphQL mutation

        Args:
            mutation: GraphQL mutation string
            variables: Variables for the mutation

        Returns:
            Response data dictionary
        """
        payload = {
            "query": mutation,
            "variables": variables
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                print(f"GraphQL mutation errors: {data['errors']}")
                return {"success": False, "errors": data["errors"]}

            return {"success": True, "data": data.get("data", {})}

        except requests.exceptions.RequestException as e:
            print(f"Error executing GraphQL mutation: {e}")
            return {"success": False, "error": str(e)}

    def batch_execute(self, mutation: str, items: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Execute mutations for multiple items

        Args:
            mutation: GraphQL mutation template
            items: List of data items to send as mutations

        Returns:
            List of response dictionaries
        """
        results = []

        for item in items:
            # Prepare variables - wrap item in expected structure
            variables = {"data": item} if "data" not in item else item

            result = self.execute_mutation(mutation, variables)
            results.append({
                "input": item,
                "response": result
            })

        return results


class MutationMapper:
    """Maps log data to GraphQL mutation variables"""

    def __init__(self, mutation_template: str):
        """
        Initialize mutation mapper

        Args:
            mutation_template: GraphQL mutation template string
        """
        self.mutation_template = mutation_template

    def map_log_to_variables(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map log data to GraphQL mutation variables

        Args:
            log_data: Extracted log data

        Returns:
            Variables dictionary for GraphQL mutation
        """
        # Remove internal fields
        variables = {k: v for k, v in log_data.items() if not k.startswith('_')}

        return variables

    def create_mutation_input(self, log_data: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """
        Create mutation and variables from log data

        Args:
            log_data: Extracted log data

        Returns:
            Tuple of (mutation_string, variables_dict)
        """
        variables = self.map_log_to_variables(log_data)
        return self.mutation_template, variables
