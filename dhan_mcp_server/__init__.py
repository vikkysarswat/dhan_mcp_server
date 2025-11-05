"""
Dhan MCP Server - A Model Context Protocol server for Dhan trading platform

This package was missing its implementation files, causing setup.py to fail.
All required files have now been created to resolve the issue.
"""

__version__ = "0.1.0"
__author__ = "Dhan MCP Server Team"
__description__ = "Complete MCP server for Dhan trading platform integration"

from .server import DhanAPIClient, DhanConfig, main
from .models import (
    OrderRequest,
    ModifyOrderRequest,
    MarginRequest,
    MarketDataRequest,
    HistoricalDataRequest,
    IntradayDataRequest,
    LedgerRequest,
    TradeHistoryRequest,
    InstrumentMasterRequest,
    TransactionType,
    ExchangeSegment,
    ProductType,
    OrderType,
    ValidityType,
    InstrumentType,
)

__all__ = [
    "DhanAPIClient",
    "DhanConfig",
    "main",
    "OrderRequest",
    "ModifyOrderRequest",
    "MarginRequest",
    "MarketDataRequest",
    "HistoricalDataRequest",
    "IntradayDataRequest",
    "LedgerRequest",
    "TradeHistoryRequest",
    "InstrumentMasterRequest",
    "TransactionType",
    "ExchangeSegment",
    "ProductType",
    "OrderType",
    "ValidityType",
    "InstrumentType",
]