"""
Web search tool for gathering information
"""
import asyncio
from typing import Dict, Any, List
from datetime import datetime


def create_web_search_tool():
    """
    Create a web search tool for Claude

    Note: This is a simplified implementation. In production, you would:
    - Integrate with actual search APIs (Google, Bing, DuckDuckGo)
    - Use the WebSearch tool from Claude Agent SDK
    - Implement rate limiting and caching
    """

    async def web_search(args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search the web for information

        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            source_type: Type of sources to search (web, academic, news, docs)

        Returns:
            Dictionary with search results
        """
        query = args.get("query", "")
        max_results = args.get("max_results", 10)
        source_type = args.get("source_type", "web")

        if not query:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: Query cannot be empty"
                }]
            }

        # NOTE: This is a mock implementation
        # In a real implementation, you would use actual search APIs
        # For Claude Agent SDK, you can use the built-in WebSearch tool

        results = {
            "query": query,
            "source_type": source_type,
            "results": [
                {
                    "title": f"Result {i+1} for: {query}",
                    "url": f"https://example.com/result_{i+1}",
                    "snippet": f"This is a sample snippet for result {i+1} about {query}. "
                              f"In production, this would contain actual search results.",
                    "timestamp": datetime.utcnow().isoformat(),
                    "relevance_score": 0.9 - (i * 0.1)
                }
                for i in range(min(max_results, 5))  # Mock data, max 5 results
            ],
            "total_results": min(max_results, 5),
            "search_time_ms": 123
        }

        return {
            "content": [{
                "type": "text",
                "text": f"Found {results['total_results']} results for query: {query}\n\n" +
                       "\n\n".join([
                           f"**{r['title']}**\n{r['url']}\n{r['snippet']}"
                           for r in results['results']
                       ])
            }],
            "metadata": results
        }

    # Return tool definition compatible with Claude Agent SDK
    return {
        "name": "web_search",
        "description": "Search the web for information on a given query. "
                      "Returns relevant sources with URLs, titles, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                },
                "source_type": {
                    "type": "string",
                    "enum": ["web", "academic", "news", "docs"],
                    "description": "Type of sources to search",
                    "default": "web"
                }
            },
            "required": ["query"]
        },
        "function": web_search
    }


async def search_multiple_queries(queries: List[str], max_results_per_query: int = 10) -> Dict[str, Any]:
    """
    Search multiple queries in parallel

    Args:
        queries: List of search queries
        max_results_per_query: Maximum results per query

    Returns:
        Dictionary mapping queries to their results
    """
    tool = create_web_search_tool()
    search_fn = tool["function"]

    # Execute searches in parallel
    tasks = [
        search_fn({
            "query": query,
            "max_results": max_results_per_query
        })
        for query in queries
    ]

    results = await asyncio.gather(*tasks)

    return {
        query: result
        for query, result in zip(queries, results)
    }


def extract_sources_from_results(search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract source information from search results

    Args:
        search_results: Results from web_search

    Returns:
        List of source dictionaries
    """
    if "metadata" in search_results and "results" in search_results["metadata"]:
        return [
            {
                "url": r["url"],
                "title": r["title"],
                "snippet": r["snippet"],
                "timestamp": r["timestamp"],
                "reliability_score": r.get("relevance_score", 0.5),
                "source_type": search_results["metadata"].get("source_type", "web")
            }
            for r in search_results["metadata"]["results"]
        ]
    return []
