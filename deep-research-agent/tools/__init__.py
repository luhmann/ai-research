"""
Custom tools for the Deep Research Agent
"""
from .web_search import create_web_search_tool
from .document import create_document_processor_tool
from .citation import create_citation_manager_tool

__all__ = [
    'create_web_search_tool',
    'create_document_processor_tool',
    'create_citation_manager_tool'
]
