"""
PubMed MCP服务 - 提供与PubMed数据库交互的多通道平台服务
"""

from .pubmed_api import PubMedAPI
from .analysis import PubMedAnalyzer
from .mcp_handler import MCPHandler

__version__ = "0.1.0"
__author__ = "PubMed MCP Team"