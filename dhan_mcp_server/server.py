#!/usr/bin/env python3
"""
Dhan MCP Server
A Model Context Protocol server for Dhan trading platform integration.
"""
import os
from dotenv import load_dotenv
import os
import pandas as pd   # NEW
from dotenv import load_dotenv
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
import httpx
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)
from pydantic import BaseModel, Field

load_dotenv()  # Add this line after imports


access_token = os.getenv("DHAN_ACCESS_TOKEN")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dhan-mcp")

# Dhan API Configuration
DHAN_BASE_URL = "https://api.dhan.co/v2"
DHAN_AUTH_URL = "https://auth.dhan.co"

COMMON_IDS = {           # NEW - shortcut for popular stocks
    "reliance": "2885",  # NSE_EQ SecurityId for Reliance
    "tcs": "11536",
    "infosys": "1594",
    "hdfcbank": "1333"
}

class DhanConfig(BaseModel):
    """Configuration for Dhan API"""
    access_token: str = access_token
    base_url: str = Field(default=DHAN_BASE_URL, description="Dhan API base URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")


class DhanAPIClient:
    """Dhan API client for making authenticated requests"""

    def __init__(self, config: DhanConfig):
        self.config = config
        self.session = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "access-token": config.access_token,
                "Content-Type": "application/json"
            }
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to Dhan API"""
        try:
            response = await self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request to Dhan API"""
        try:
            response = await self.session.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request to Dhan API"""
        try:
            response = await self.session.put(endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    async def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make DELETE request to Dhan API"""
        try:
            response = await self.session.delete(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise


# Initialize MCP server
server = Server("dhan-mcp-server")

# Configuration (will be loaded from environment or config file)
config = None
api_client = None

# --------------------------
# Instrument Master Cache
# --------------------------
async def load_instruments() -> pd.DataFrame:
    """Load instrument master CSV into memory (cached)."""
    global INSTRUMENT_CACHE
    if INSTRUMENT_CACHE is None:
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        logger.info("Downloading instrument master CSV...")
        df = pd.read_csv(url)
        df["SM_SYMBOL_NAME"] = df["SM_SYMBOL_NAME"].astype(str).str.lower()
        df["SEM_CUSTOM_SYMBOL"] = df["SEM_CUSTOM_SYMBOL"].astype(str).str.lower()
        df["SEM_TRADING_SYMBOL"] = df["SEM_TRADING_SYMBOL"].astype(str).str.lower()
        INSTRUMENT_CACHE = df
        logger.info(f"Instrument cache loaded: {len(df)} rows")
    return INSTRUMENT_CACHE


async def fast_search_instrument(query: str, limit: int = 5):
    """Search cached instruments quickly."""
    df = await load_instruments()
    q = query.lower()
    matches = df[
        df["SM_SYMBOL_NAME"].str.contains(q, na=False) |
        df["SEM_CUSTOM_SYMBOL"].str.contains(q, na=False) |
        df["SEM_TRADING_SYMBOL"].str.contains(q, na=False)
    ]
    return matches.head(limit).to_dict(orient="records")



@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="dhan://profile",
            name="User Profile",
            description="Current user profile and account information",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://positions",
            name="Trading Positions",
            description="Current trading positions",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://holdings",
            name="Holdings",
            description="Long-term holdings and investments",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://orders",
            name="Order History",
            description="Trading order history and status",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://trades",
            name="Trade History",
            description="Executed trades for the day",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://funds",
            name="Account Funds",
            description="Available funds and margin information",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://ledger",
            name="Account Ledger",
            description="Credit/debit transaction history (requires date parameters)",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://historical-trades",
            name="Historical Trades",
            description="Detailed historical trade data (requires date parameters)",
            mimeType="application/json",
        ),
        Resource(
            uri="dhan://instruments",
            name="Instrument Master",
            description="Complete instrument list with security IDs and details",
            mimeType="application/json",
        ),
    ]

# --------------------------
# Tools
# --------------------------

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a specific resource"""
    if not api_client:
        raise Exception("Dhan API client not initialized")

    try:
        if uri == "dhan://profile":
            data = await api_client.get("/profile")
            return json.dumps(data, indent=2)
        elif uri == "dhan://positions":
            # TODO: Implement when positions endpoint is available
            return json.dumps({"message": "Positions endpoint not yet implemented"}, indent=2)
        elif uri == "dhan://holdings":
            # TODO: Implement when holdings endpoint is available
            return json.dumps({"message": "Holdings endpoint not yet implemented"}, indent=2)
        elif uri == "dhan://orders":
            data = await api_client.get("/orders")
            return json.dumps(data, indent=2)
        elif uri == "dhan://trades":
            data = await api_client.get("/trades")
            return json.dumps(data, indent=2)
        elif uri == "dhan://funds":
            data = await api_client.get("/fundlimit")
            return json.dumps(data, indent=2)
        else:
            raise Exception(f"Unknown resource: {uri}")
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_profile",
            description="Get user profile and account information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="validate_token",
            description="Validate the current access token",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="place_order",
            description="Place a new trading order",
            inputSchema={
                "type": "object",
                "properties": {
                    "dhanClientId": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    },
                    "correlationId": {
                        "type": "string",
                        "description": "User/partner generated id for tracking back (optional)"
                    },
                    "transactionType": {
                        "type": "string",
                        "enum": ["BUY", "SELL"],
                        "description": "The trading side of transaction"
                    },
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "NSE_CURR", "BSE_EQ", "BSE_FNO", "BSE_CURR", "MCX_COMM"],
                        "description": "Exchange Segment"
                    },
                    "productType": {
                        "type": "string",
                        "enum": ["CNC", "INTRADAY", "MARGIN", "MTF", "CO", "BO"],
                        "description": "Product type"
                    },
                    "orderType": {
                        "type": "string",
                        "enum": ["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_MARKET"],
                        "description": "Order Type"
                    },
                    "validity": {
                        "type": "string",
                        "enum": ["DAY", "IOC"],
                        "description": "Validity of Order"
                    },
                    "securityId": {
                        "type": "string",
                        "description": "Exchange standard ID for each scrip"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares for the order"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price at which order is placed (required for LIMIT orders)"
                    },
                    "triggerPrice": {
                        "type": "number",
                        "description": "Price at which order is triggered (for SL orders)"
                    },
                    "disclosedQuantity": {
                        "type": "integer",
                        "description": "Number of shares visible (keep more than 30% of quantity)"
                    },
                    "afterMarketOrder": {
                        "type": "boolean",
                        "description": "Flag for orders placed after market hours",
                        "default": False
                    },
                    "amoTime": {
                        "type": "string",
                        "enum": ["PRE_OPEN", "OPEN", "OPEN_30", "OPEN_60"],
                        "description": "Timing to pump the after market order"
                    },
                    "boProfitValue": {
                        "type": "number",
                        "description": "Bracket Order Target Price change"
                    },
                    "boStopLossValue": {
                        "type": "number",
                        "description": "Bracket Order Stop Loss Price change"
                    }
                },
                "required": ["dhanClientId", "transactionType", "exchangeSegment", "productType", "orderType",
                             "validity", "securityId", "quantity"],
            },
        ),
        Tool(
            name="get_ltp_by_symbol",
            description="Fetch Last Traded Price (LTP) directly by symbol or company name. Uses cached instrument master for fast lookup.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Company symbol or name, e.g. 'Reliance'"},
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "BSE_EQ"],
                        "default": "NSE_EQ"
                    },
                    "client_id": {"type": "string", "description": "Dhan client ID"}
                },
                "required": ["query", "client_id"]
            }
            ),
        Tool(
            name="modify_order",
            description="Modify a pending order",
            inputSchema={
                "type": "object",
                "properties": {
                    "dhanClientId": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    },
                    "orderId": {
                        "type": "string",
                        "description": "Order specific identification generated by Dhan"
                    },
                    "orderType": {
                        "type": "string",
                        "enum": ["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_MARKET"],
                        "description": "Order Type"
                    },
                    "legName": {
                        "type": "string",
                        "enum": ["ENTRY_LEG", "TARGET_LEG", "STOP_LOSS_LEG"],
                        "description": "In case of BO & CO, which leg is modified"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity to be modified"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price to be modified"
                    },
                    "disclosedQuantity": {
                        "type": "integer",
                        "description": "Number of shares visible"
                    },
                    "triggerPrice": {
                        "type": "number",
                        "description": "Trigger price for SL orders"
                    },
                    "validity": {
                        "type": "string",
                        "enum": ["DAY", "IOC"],
                        "description": "Validity of Order"
                    }
                },
                "required": ["dhanClientId", "orderId", "orderType", "validity"],
            },
        ),
        Tool(
            name="cancel_order",
            description="Cancel a pending order",
            inputSchema={
                "type": "object",
                "properties": {
                    "orderId": {
                        "type": "string",
                        "description": "Order specific identification generated by Dhan"
                    }
                },
                "required": ["orderId"],
            },
        ),
        Tool(
            name="slice_order",
            description="Slice order into multiple legs over freeze limit",
            inputSchema={
                "type": "object",
                "properties": {
                    "dhanClientId": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    },
                    "correlationId": {
                        "type": "string",
                        "description": "User/partner generated id for tracking back (optional)"
                    },
                    "transactionType": {
                        "type": "string",
                        "enum": ["BUY", "SELL"],
                        "description": "The trading side of transaction"
                    },
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "NSE_CURR", "BSE_EQ", "BSE_FNO", "BSE_CURR", "MCX_COMM"],
                        "description": "Exchange Segment"
                    },
                    "productType": {
                        "type": "string",
                        "enum": ["CNC", "INTRADAY", "MARGIN", "MTF", "CO", "BO"],
                        "description": "Product type"
                    },
                    "orderType": {
                        "type": "string",
                        "enum": ["LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_MARKET"],
                        "description": "Order Type"
                    },
                    "validity": {
                        "type": "string",
                        "enum": ["DAY", "IOC"],
                        "description": "Validity of Order"
                    },
                    "securityId": {
                        "type": "string",
                        "description": "Exchange standard ID for each scrip"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares for the order (will be sliced)"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price at which order is placed"
                    },
                    "triggerPrice": {
                        "type": "number",
                        "description": "Price at which order is triggered"
                    },
                    "disclosedQuantity": {
                        "type": "integer",
                        "description": "Number of shares visible"
                    },
                    "afterMarketOrder": {
                        "type": "boolean",
                        "description": "Flag for orders placed after market hours",
                        "default": False
                    },
                    "amoTime": {
                        "type": "string",
                        "enum": ["PRE_OPEN", "OPEN", "OPEN_30", "OPEN_60"],
                        "description": "Timing to pump the after market order"
                    },
                    "boProfitValue": {
                        "type": "number",
                        "description": "Bracket Order Target Price change"
                    },
                    "boStopLossValue": {
                        "type": "number",
                        "description": "Bracket Order Stop Loss Price change"
                    }
                },
                "required": ["dhanClientId", "transactionType", "exchangeSegment", "productType", "orderType",
                             "validity", "securityId", "quantity"],
            },
        ),
        Tool(
            name="get_orders",
            description="Retrieve the list of all orders for the day",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_order_by_id",
            description="Retrieve the status of a specific order by order ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "orderId": {
                        "type": "string",
                        "description": "Order specific identification generated by Dhan"
                    }
                },
                "required": ["orderId"],
            },
        ),
        Tool(
            name="get_order_by_correlation_id",
            description="Retrieve the status of an order by correlation ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "correlationId": {
                        "type": "string",
                        "description": "User/partner generated id for tracking back"
                    }
                },
                "required": ["correlationId"],
            },
        ),
        Tool(
            name="get_trades",
            description="Retrieve the list of all trades for the day",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_trades_by_order_id",
            description="Retrieve trade details for a specific order ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "orderId": {
                        "type": "string",
                        "description": "Order specific identification generated by Dhan"
                    }
                },
                "required": ["orderId"],
            },
        ),
        Tool(
            name="calculate_margin",
            description="Calculate margin requirement for any order before placing it",
            inputSchema={
                "type": "object",
                "properties": {
                    "dhanClientId": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    },
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "BSE_EQ", "BSE_FNO", "MCX_COMM"],
                        "description": "Exchange & Segment"
                    },
                    "transactionType": {
                        "type": "string",
                        "enum": ["BUY", "SELL"],
                        "description": "The trading side of transaction"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of shares for the order"
                    },
                    "productType": {
                        "type": "string",
                        "enum": ["CNC", "INTRADAY", "MARGIN", "MTF", "CO", "BO"],
                        "description": "Product type"
                    },
                    "securityId": {
                        "type": "string",
                        "description": "Exchange standard ID for each scrip"
                    },
                    "price": {
                        "type": "number",
                        "description": "Price at which order is placed"
                    },
                    "triggerPrice": {
                        "type": "number",
                        "description": "Price at which order is triggered (for SL orders)"
                    }
                },
                "required": ["dhanClientId", "exchangeSegment", "transactionType", "quantity", "productType",
                             "securityId", "price"],
            },
        ),
        Tool(
            name="get_fund_limits",
            description="Get trading account fund information including available balance, margins, etc.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_ledger",
            description="Retrieve Trading Account ledger report with credit/debit details",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    }
                },
                "required": ["from_date", "to_date"],
            },
        ),
        Tool(
            name="get_historical_trades",
            description="Retrieve detailed historical trade data for a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (0 for first page)",
                        "default": 0,
                        "minimum": 0
                    }
                },
                "required": ["from_date", "to_date"],
            },
        ),
        Tool(
            name="get_market_ltp",
            description="Get Last Traded Price (LTP) for multiple instruments",
            inputSchema={
                "type": "object",
                "properties": {
                    "instruments": {
                        "type": "object",
                        "description": "Instruments grouped by exchange segment",
                        "additionalProperties": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "client_id": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    }
                },
                "required": ["instruments", "client_id"],
            },
        ),
        Tool(
            name="get_market_ohlc",
            description="Get OHLC (Open, High, Low, Close) data for multiple instruments",
            inputSchema={
                "type": "object",
                "properties": {
                    "instruments": {
                        "type": "object",
                        "description": "Instruments grouped by exchange segment",
                        "additionalProperties": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "client_id": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    }
                },
                "required": ["instruments", "client_id"],
            },
        ),
        Tool(
            name="get_market_depth",
            description="Get market depth with full quote data including order book",
            inputSchema={
                "type": "object",
                "properties": {
                    "instruments": {
                        "type": "object",
                        "description": "Instruments grouped by exchange segment",
                        "additionalProperties": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "client_id": {
                        "type": "string",
                        "description": "User specific identification generated by Dhan"
                    }
                },
                "required": ["instruments", "client_id"],
            },
        ),
        Tool(
            name="get_historical_data",
            description="Get daily historical OHLC data for an instrument",
            inputSchema={
                "type": "object",
                "properties": {
                    "securityId": {
                        "type": "string",
                        "description": "Exchange standard ID for the instrument"
                    },
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "BSE_EQ", "BSE_FNO", "MCX_COMM"],
                        "description": "Exchange & segment"
                    },
                    "instrument": {
                        "type": "string",
                        "enum": ["EQUITY", "DERIVATIVES"],
                        "description": "Instrument type"
                    },
                    "fromDate": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "toDate": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                    },
                    "expiryCode": {
                        "type": "integer",
                        "description": "Expiry code for derivatives (optional)",
                        "default": 0
                    },
                    "oi": {
                        "type": "boolean",
                        "description": "Include Open Interest data",
                        "default": False
                    }
                },
                "required": ["securityId", "exchangeSegment", "instrument", "fromDate", "toDate"],
            },
        ),
        Tool(
            name="get_intraday_data",
            description="Get intraday OHLC data with minute-level granularity",
            inputSchema={
                "type": "object",
                "properties": {
                    "securityId": {
                        "type": "string",
                        "description": "Exchange standard ID for the instrument"
                    },
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "BSE_EQ", "BSE_FNO", "MCX_COMM"],
                        "description": "Exchange & segment"
                    },
                    "instrument": {
                        "type": "string",
                        "enum": ["EQUITY", "DERIVATIVES"],
                        "description": "Instrument type"
                    },
                    "interval": {
                        "type": "string",
                        "enum": ["1", "5", "15", "25", "60"],
                        "description": "Minute intervals (1, 5, 15, 25, 60)"
                    },
                    "fromDate": {
                        "type": "string",
                        "description": "Start datetime in YYYY-MM-DD HH:MM:SS format"
                    },
                    "toDate": {
                        "type": "string",
                        "description": "End datetime in YYYY-MM-DD HH:MM:SS format"
                    },
                    "oi": {
                        "type": "boolean",
                        "description": "Include Open Interest data",
                        "default": False
                    }
                },
                "required": ["securityId", "exchangeSegment", "instrument", "interval", "fromDate", "toDate"],
            },
        ),
        Tool(
            name="get_instrument_master",
            description="Get complete instrument master list or segment-wise list",
            inputSchema={
                "type": "object",
                "properties": {
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "NSE_CURR", "BSE_EQ", "BSE_FNO", "BSE_CURR", "MCX_COMM"],
                        "description": "Exchange segment (optional - if not provided, returns complete list)"
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Get detailed instrument list with all columns",
                        "default": False
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="search_instruments",
            description="Search for instruments by symbol name or display name",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (symbol name, company name, etc.)"
                    },
                    "exchangeSegment": {
                        "type": "string",
                        "enum": ["NSE_EQ", "NSE_FNO", "NSE_CURR", "BSE_EQ", "BSE_FNO", "BSE_CURR", "MCX_COMM"],
                        "description": "Filter by exchange segment (optional)"
                    },
                    "instrument": {
                        "type": "string",
                        "enum": ["EQUITY", "OPTIDX", "FUTIDX", "FUTSTK", "OPTSTK"],
                        "description": "Filter by instrument type (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 20,
                        "maximum": 100
                    }
                },
                "required": ["query"],
            },
        ),
        # TODO: Add more tools for market data and portfolio
        # - get_positions
        # - get_holdings
        # - get_quotes
        # - get_historical_data
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Execute a tool"""
    if not api_client:
        return [TextContent(type="text", text="Error: Dhan API client not initialized")]

    try:
        if name == "get_profile":
            data = await api_client.get("/profile")
            return [TextContent(
                type="text",
                text=f"Profile Information:\n{json.dumps(data, indent=2)}"
            )]

        elif name == "get_ltp_by_symbol":
            query = arguments["query"].lower()
            exchange = arguments.get("exchangeSegment", "NSE_EQ")
            client_id = arguments["client_id"]

            # Step 1: Shortcut if in COMMON_IDS
            sec_id = COMMON_IDS.get(query)
            if not sec_id:
                # Step 2: Search cached instruments
                results = await fast_search_instrument(query)
                if not results:
                    return [TextContent(type="text", text=f"No match for {query}")]
                sec_id = results[0].get("SEM_SMST_SECURITY_ID") or results[0].get("SEM_EXM_EXCH_ID")

            # Step 3: Fetch LTP
            resp = await api_client.session.post(
                "/marketfeed/ltp",
                json={exchange: [int(sec_id)]},
                headers={**api_client.session.headers, "client-id": client_id}
            )
            resp.raise_for_status()
            data = resp.json()

            ltp = None
            if data.get("status") == "success":
                ltp = list(data["data"][exchange].values())[0].get("last_price")

            return [TextContent(type="text", text=f"{query.upper()} LTP: ₹{ltp}" if ltp else "No LTP data")]


        elif name == "validate_token":
            data = await api_client.get("/profile")
            validity = data.get("tokenValidity", "Unknown")
            client_id = data.get("dhanClientId", "Unknown")
            segments = data.get("activeSegment", "Unknown")
            return [TextContent(
                type="text",
                text=f"Token Status:\nClient ID: {client_id}\nValid until: {validity}\nActive Segments: {segments}"
            )]

        elif name == "place_order":
            # Clean the arguments to remove None values and empty strings
            order_data = {k: v for k, v in arguments.items() if v is not None and v != ""}

            # Convert numeric strings to proper types
            if "quantity" in order_data:
                order_data["quantity"] = str(order_data["quantity"])
            if "price" in order_data and order_data["price"] != "":
                order_data["price"] = str(order_data["price"])
            if "triggerPrice" in order_data and order_data["triggerPrice"] != "":
                order_data["triggerPrice"] = str(order_data["triggerPrice"])
            if "disclosedQuantity" in order_data and order_data["disclosedQuantity"] != "":
                order_data["disclosedQuantity"] = str(order_data["disclosedQuantity"])

            # Set empty strings for optional fields that aren't provided
            optional_fields = ["correlationId", "price", "triggerPrice", "disclosedQuantity", "amoTime",
                               "boProfitValue", "boStopLossValue"]
            for field in optional_fields:
                if field not in order_data:
                    order_data[field] = ""

            # Set default values
            order_data.setdefault("afterMarketOrder", False)

            data = await api_client.post("/orders", order_data)
            return [TextContent(
                type="text",
                text=f"Order Placed Successfully:\nOrder ID: {data.get('orderId')}\nStatus: {data.get('orderStatus')}"
            )]

        elif name == "modify_order":
            order_id = arguments.pop("orderId")
            modify_data = {k: v for k, v in arguments.items() if v is not None and v != ""}

            # Convert numeric fields to strings as expected by API
            if "quantity" in modify_data:
                modify_data["quantity"] = str(modify_data["quantity"])
            if "price" in modify_data:
                modify_data["price"] = str(modify_data["price"])
            if "triggerPrice" in modify_data:
                modify_data["triggerPrice"] = str(modify_data["triggerPrice"])
            if "disclosedQuantity" in modify_data:
                modify_data["disclosedQuantity"] = str(modify_data["disclosedQuantity"])

            # Set empty strings for optional fields
            optional_fields = ["legName", "triggerPrice", "disclosedQuantity"]
            for field in optional_fields:
                if field not in modify_data:
                    modify_data[field] = ""

            data = await api_client.put(f"/orders/{order_id}", modify_data)
            return [TextContent(
                type="text",
                text=f"Order Modified Successfully:\nOrder ID: {data.get('orderId')}\nStatus: {data.get('orderStatus')}"
            )]

        elif name == "cancel_order":
            order_id = arguments["orderId"]
            data = await api_client.delete(f"/orders/{order_id}")
            return [TextContent(
                type="text",
                text=f"Order Cancelled:\nOrder ID: {data.get('orderId')}\nStatus: {data.get('orderStatus')}"
            )]

        elif name == "slice_order":
            # Clean the arguments similar to place_order
            order_data = {k: v for k, v in arguments.items() if v is not None and v != ""}

            # Convert numeric strings to proper types
            if "quantity" in order_data:
                order_data["quantity"] = str(order_data["quantity"])
            if "price" in order_data and order_data["price"] != "":
                order_data["price"] = str(order_data["price"])
            if "triggerPrice" in order_data and order_data["triggerPrice"] != "":
                order_data["triggerPrice"] = str(order_data["triggerPrice"])
            if "disclosedQuantity" in order_data and order_data["disclosedQuantity"] != "":
                order_data["disclosedQuantity"] = str(order_data["disclosedQuantity"])

            # Set empty strings for optional fields
            optional_fields = ["correlationId", "price", "triggerPrice", "disclosedQuantity", "amoTime",
                               "boProfitValue", "boStopLossValue"]
            for field in optional_fields:
                if field not in order_data:
                    order_data[field] = ""

            order_data.setdefault("afterMarketOrder", False)

            data = await api_client.post("/orders/slicing", order_data)
            order_ids = [order.get('orderId') for order in data]
            return [TextContent(
                type="text",
                text=f"Orders Sliced Successfully:\n{json.dumps(data, indent=2)}\nOrder IDs: {', '.join(order_ids)}"
            )]

        elif name == "get_orders":
            data = await api_client.get("/orders")
            if isinstance(data, list) and len(data) > 0:
                summary = f"Total Orders: {len(data)}\n\n"
                for order in data[:10]:  # Show first 10 orders
                    summary += f"Order ID: {order.get('orderId')}\n"
                    summary += f"Symbol: {order.get('tradingSymbol', 'N/A')}\n"
                    summary += f"Type: {order.get('transactionType')} {order.get('quantity')} @ {order.get('price', 'Market')}\n"
                    summary += f"Status: {order.get('orderStatus')}\n"
                    summary += f"Time: {order.get('createTime')}\n\n"

                if len(data) > 10:
                    summary += f"... and {len(data) - 10} more orders"

                return [TextContent(type="text", text=summary)]
            else:
                return [TextContent(type="text", text="No orders found for today")]

        elif name == "get_order_by_id":
            order_id = arguments["orderId"]
            data = await api_client.get(f"/orders/{order_id}")
            return [TextContent(
                type="text",
                text=f"Order Details:\n{json.dumps(data, indent=2)}"
            )]

        elif name == "get_order_by_correlation_id":
            correlation_id = arguments["correlationId"]
            data = await api_client.get(f"/orders/external/{correlation_id}")
            return [TextContent(
                type="text",
                text=f"Order Details:\n{json.dumps(data, indent=2)}"
            )]

        elif name == "get_trades":
            data = await api_client.get("/trades")
            if isinstance(data, list) and len(data) > 0:
                summary = f"Total Trades: {len(data)}\n\n"
                total_value = 0
                for trade in data[:10]:  # Show first 10 trades
                    trade_value = trade.get('tradedQuantity', 0) * trade.get('tradedPrice', 0)
                    total_value += trade_value
                    summary += f"Order ID: {trade.get('orderId')}\n"
                    summary += f"Symbol: {trade.get('tradingSymbol', 'N/A')}\n"
                    summary += f"Trade: {trade.get('transactionType')} {trade.get('tradedQuantity')} @ ₹{trade.get('tradedPrice')}\n"
                    summary += f"Value: ₹{trade_value:.2f}\n"
                    summary += f"Time: {trade.get('exchangeTime')}\n\n"

                if len(data) > 10:
                    summary += f"... and {len(data) - 10} more trades\n"

                summary += f"Total Value (first 10): ₹{total_value:.2f}"
                return [TextContent(type="text", text=summary)]
            else:
                return [TextContent(type="text", text="No trades found for today")]

        elif name == "get_trades_by_order_id":
            order_id = arguments["orderId"]
            data = await api_client.get(f"/trades/{order_id}")
            if isinstance(data, list):
                return [TextContent(
                    type="text",
                    text=f"Trades for Order ID {order_id}:\n{json.dumps(data, indent=2)}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Trade Details for Order ID {order_id}:\n{json.dumps(data, indent=2)}"
                )]

        elif name == "calculate_margin":
            # Prepare margin calculation data
            margin_data = {k: v for k, v in arguments.items() if v is not None}

            # Ensure triggerPrice is included (set to 0 if not provided)
            if "triggerPrice" not in margin_data:
                margin_data["triggerPrice"] = 0

            data = await api_client.post("/margincalculator", margin_data)

            # Format the response nicely
            response_text = "Margin Calculation Result:\n"
            response_text += f"Total Margin Required: ₹{data.get('totalMargin', 0):.2f}\n"
            response_text += f"Available Balance: ₹{data.get('availableBalance', 0):.2f}\n"
            response_text += f"Span Margin: ₹{data.get('spanMargin', 0):.2f}\n"
            response_text += f"Exposure Margin: ₹{data.get('exposureMargin', 0):.2f}\n"
            response_text += f"Variable Margin: ₹{data.get('variableMargin', 0):.2f}\n"
            response_text += f"Brokerage: ₹{data.get('brokerage', 0):.2f}\n"
            response_text += f"Leverage: {data.get('leverage', 'N/A')}x\n"

            insufficient = data.get('insufficientBalance', 0)
            if insufficient > 0:
                response_text += f"⚠️ Insufficient Balance: ₹{insufficient:.2f}\n"
            else:
                response_text += "✅ Sufficient balance available\n"

            return [TextContent(type="text", text=response_text)]

        elif name == "get_ledger":
            from_date = arguments["from_date"]
            to_date = arguments["to_date"]
            params = {"from-date": from_date, "to-date": to_date}

            data = await api_client.get("/ledger", params=params)

            if isinstance(data, list) and len(data) > 0:
                response_text = f"Ledger Report ({from_date} to {to_date}):\n"
                response_text += f"Total Entries: {len(data)}\n\n"

                total_credits = sum(float(entry.get('credit', 0)) for entry in data)
                total_debits = sum(float(entry.get('debit', 0)) for entry in data)

                response_text += f"Summary:\n"
                response_text += f"Total Credits: ₹{total_credits:,.2f}\n"
                response_text += f"Total Debits: ₹{total_debits:,.2f}\n"
                response_text += f"Net: ₹{(total_credits - total_debits):,.2f}\n\n"

                response_text += "Recent Entries:\n"
                for entry in data[:10]:  # Show first 10 entries
                    response_text += f"Date: {entry.get('voucherdate')}\n"
                    response_text += f"Description: {entry.get('narration')}\n"
                    response_text += f"Type: {entry.get('voucherdesc')}\n"
                    if float(entry.get('credit', 0)) > 0:
                        response_text += f"Credit: ₹{float(entry.get('credit')):,.2f}\n"
                    if float(entry.get('debit', 0)) > 0:
                        response_text += f"Debit: ₹{float(entry.get('debit')):,.2f}\n"
                    response_text += f"Balance: ₹{float(entry.get('runbal', 0)):,.2f}\n\n"

                if len(data) > 10:
                    response_text += f"... and {len(data) - 10} more entries"

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text=f"No ledger entries found for {from_date} to {to_date}")]

        elif name == "get_historical_trades":
            from_date = arguments["from_date"]
            to_date = arguments["to_date"]
            page = arguments.get("page", 0)

            endpoint = f"/trades/{from_date}/{to_date}/{page}"
            data = await api_client.get(endpoint)

            if isinstance(data, list) and len(data) > 0:
                response_text = f"Historical Trades ({from_date} to {to_date}, Page {page}):\n"
                response_text += f"Total Trades: {len(data)}\n\n"

                total_value = 0
                for trade in data:
                    trade_value = trade.get('tradedQuantity', 0) * trade.get('tradedPrice', 0)
                    total_value += trade_value

                response_text += f"Total Trade Value: ₹{total_value:,.2f}\n\n"

                response_text += "Trade Details:\n"
                for trade in data[:10]:  # Show first 10 trades
                    trade_value = trade.get('tradedQuantity', 0) * trade.get('tradedPrice', 0)
                    response_text += f"Symbol: {trade.get('customSymbol', 'N/A')}\n"
                    response_text += f"Trade: {trade.get('transactionType')} {trade.get('tradedQuantity')} @ ₹{trade.get('tradedPrice')}\n"
                    response_text += f"Value: ₹{trade_value:.2f}\n"
                    response_text += f"Time: {trade.get('exchangeTime')}\n"
                    response_text += f"Charges: STT: ₹{trade.get('stt', 0)}, Brokerage: ₹{trade.get('brokerageCharges', 0)}\n\n"

                if len(data) > 10:
                    response_text += f"... and {len(data) - 10} more trades"

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text=f"No historical trades found for {from_date} to {to_date}")]

        elif name in ["get_market_ltp", "get_market_ohlc", "get_market_depth"]:
            instruments = arguments["instruments"]
            client_id = arguments["client_id"]

            # Map tool name to API endpoint
            endpoint_map = {
                "get_market_ltp": "/marketfeed/ltp",
                "get_market_ohlc": "/marketfeed/ohlc",
                "get_market_depth": "/marketfeed/quote"
            }

            endpoint = endpoint_map[name]

            # Add client-id header for market data requests
            headers = {"client-id": client_id}

            # Convert security IDs to integers for API request
            api_instruments = {}
            for segment, ids in instruments.items():
                api_instruments[segment] = [int(id) for id in ids]

            # Make request with custom headers
            response = await api_client.session.post(
                endpoint,
                json=api_instruments,
                headers={**api_client.session.headers, **headers}
            )
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "success" and "data" in data:
                response_text = f"Market Data ({name.replace('get_market_', '').upper()}):\n\n"

                for segment, segment_data in data["data"].items():
                    response_text += f"{segment}:\n"
                    for security_id, quotes in segment_data.items():
                        response_text += f"  Security ID {security_id}:\n"

                        if "last_price" in quotes:
                            response_text += f"    LTP: ₹{quotes['last_price']}\n"

                        if "ohlc" in quotes:
                            ohlc = quotes["ohlc"]
                            response_text += f"    Open: ₹{ohlc.get('open', 0)}\n"
                            response_text += f"    High: ₹{ohlc.get('high', 0)}\n"
                            response_text += f"    Low: ₹{ohlc.get('low', 0)}\n"
                            response_text += f"    Close: ₹{ohlc.get('close', 0)}\n"

                        if "volume" in quotes:
                            response_text += f"    Volume: {quotes['volume']:,}\n"

                        if "depth" in quotes:
                            depth = quotes["depth"]
                            response_text += f"    Buy Qty: {quotes.get('buy_quantity', 0):,}\n"
                            response_text += f"    Sell Qty: {quotes.get('sell_quantity', 0):,}\n"

                        response_text += "\n"

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text=f"Failed to fetch market data: {data}")]

        elif name == "get_historical_data":
            historical_data = {k: v for k, v in arguments.items() if v is not None}
            data = await api_client.post("/charts/historical", historical_data)

            if "open" in data and len(data["open"]) > 0:
                response_text = f"Historical Data ({arguments['securityId']}):\n"
                response_text += f"Period: {arguments['fromDate']} to {arguments['toDate']}\n"
                response_text += f"Data Points: {len(data['open'])}\n\n"

                # Show last few data points
                for i in range(min(5, len(data["open"]))):
                    idx = len(data["open"]) - 1 - i
                    response_text += f"Date: {data['timestamp'][idx]} (epoch)\n"
                    response_text += f"OHLC: O:₹{data['open'][idx]} H:₹{data['high'][idx]} L:₹{data['low'][idx]} C:₹{data['close'][idx]}\n"
                    response_text += f"Volume: {data['volume'][idx]:,}\n\n"

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text="No historical data found for the specified period")]

        elif name == "get_intraday_data":
            intraday_data = {k: v for k, v in arguments.items() if v is not None}
            data = await api_client.post("/charts/intraday", intraday_data)

            if "open" in data and len(data["open"]) > 0:
                response_text = f"Intraday Data ({arguments['securityId']}):\n"
                response_text += f"Interval: {arguments['interval']} minute(s)\n"
                response_text += f"Period: {arguments['fromDate']} to {arguments['toDate']}\n"
                response_text += f"Data Points: {len(data['open'])}\n\n"

                # Show last few data points
                for i in range(min(5, len(data["open"]))):
                    idx = len(data["open"]) - 1 - i
                    response_text += f"Time: {data['timestamp'][idx]} (epoch)\n"
                    response_text += f"OHLC: O:₹{data['open'][idx]} H:₹{data['high'][idx]} L:₹{data['low'][idx]} C:₹{data['close'][idx]}\n"
                    response_text += f"Volume: {data['volume'][idx]:,}\n\n"

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text="No intraday data found for the specified period")]

        elif name == "get_instrument_master":
            exchange_segment = arguments.get("exchangeSegment")
            detailed = arguments.get("detailed", False)

            if exchange_segment:
                # Get segment-specific instrument list
                data = await api_client.get(f"/instrument/{exchange_segment}")
                response_text = f"Instrument Master for {exchange_segment}:\n"
                response_text += f"Total Instruments: {len(data) if isinstance(data, list) else 'Unknown'}\n\n"

                if isinstance(data, list) and len(data) > 0:
                    # Show first 10 instruments
                    for instrument in data[:10]:
                        response_text += f"Security ID: {instrument.get('SEM_EXM_EXCH_ID', 'N/A')}\n"
                        response_text += f"Symbol: {instrument.get('SEM_CUSTOM_SYMBOL', 'N/A')}\n"
                        response_text += f"Name: {instrument.get('SM_SYMBOL_NAME', 'N/A')}\n"
                        response_text += f"Instrument: {instrument.get('SEM_INSTRUMENT_NAME', 'N/A')}\n"
                        response_text += f"Lot Size: {instrument.get('SEM_LOT_UNITS', 'N/A')}\n\n"

                    if len(data) > 10:
                        response_text += f"... and {len(data) - 10} more instruments"

                return [TextContent(type="text", text=response_text)]
            else:
                # Get complete master list (CSV format)
                import httpx

                if detailed:
                    csv_url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
                else:
                    csv_url = "https://images.dhan.co/api-data/api-scrip-master.csv"

                async with httpx.AsyncClient() as client:
                    csv_response = await client.get(csv_url)
                    csv_response.raise_for_status()

                    # Parse first few lines to show sample
                    lines = csv_response.text.strip().split('\n')
                    response_text = f"Complete Instrument Master ({'Detailed' if detailed else 'Compact'}):\n"
                    response_text += f"Total Records: {len(lines) - 1}\n"  # Excluding header
                    response_text += f"Source: {csv_url}\n\n"
                    response_text += "Sample Data (First 5 records):\n"

                    # Show header and first 5 data rows
                    for i, line in enumerate(lines[:6]):
                        if i == 0:
                            response_text += f"Headers: {line}\n\n"
                        else:
                            response_text += f"Record {i}: {line}\n"

                    response_text += f"\n... and {len(lines) - 6} more records"
                    response_text += f"\n\nTo process this data, use the CSV URL: {csv_url}"

                return [TextContent(type="text", text=response_text)]

        elif name == "search_instruments":
            query = arguments["query"].lower()
            exchange_segment = arguments.get("exchangeSegment")
            instrument_type = arguments.get("instrument")
            limit = arguments.get("limit", 20)

            # First get the instrument list
            if exchange_segment:
                # Search within specific segment
                data = await api_client.get(f"/instrument/{exchange_segment}")
            else:
                # For broader search, we'll need to fetch CSV and parse
                # This is a simplified version - in production, you might cache this data
                import httpx

                async with httpx.AsyncClient() as client:
                    csv_response = await client.get("https://images.dhan.co/api-data/api-scrip-master.csv")
                    csv_response.raise_for_status()

                    # Simple CSV parsing (in production, use pandas or csv module)
                    lines = csv_response.text.strip().split('\n')
                    headers = lines[0].split(',')

                    # Convert to dict format for consistency
                    data = []
                    for line in lines[1:]:  # Skip header
                        values = line.split(',')
                        if len(values) >= len(headers):
                            record = dict(zip(headers, values))
                            data.append(record)

            # Search through the data
            matches = []
            if isinstance(data, list):
                for instrument in data:
                    # Search in symbol name and display name
                    symbol_name = str(instrument.get('SM_SYMBOL_NAME', '')).lower()
                    display_name = str(instrument.get('SEM_CUSTOM_SYMBOL', '')).lower()
                    trading_symbol = str(instrument.get('SEM_TRADING_SYMBOL', '')).lower()

                    if (query in symbol_name or query in display_name or query in trading_symbol):
                        # Apply filters
                        if exchange_segment and instrument.get('SEM_EXM_EXCH_ID') != exchange_segment:
                            continue
                        if instrument_type and instrument.get('SEM_INSTRUMENT_NAME') != instrument_type:
                            continue

                        matches.append(instrument)
                        if len(matches) >= limit:
                            break

            if matches:
                response_text = f"Search Results for '{query}':\n"
                response_text += f"Found {len(matches)} matching instruments\n\n"

                for instrument in matches:
                    response_text += f"Security ID: {instrument.get('SEM_EXM_EXCH_ID', 'N/A')}\n"
                    response_text += f"Symbol: {instrument.get('SEM_CUSTOM_SYMBOL', 'N/A')}\n"
                    response_text += f"Name: {instrument.get('SM_SYMBOL_NAME', 'N/A')}\n"
                    response_text += f"Exchange: {instrument.get('SEM_SEGMENT', 'N/A')}\n"
                    response_text += f"Instrument: {instrument.get('SEM_INSTRUMENT_NAME', 'N/A')}\n"
                    response_text += f"Lot Size: {instrument.get('SEM_LOT_UNITS', 'N/A')}\n\n"

                return [TextContent(type="text", text=response_text)]
            else:
                return [TextContent(type="text", text=f"No instruments found matching '{query}'")]

        elif name == "get_fund_limits":
            data = await api_client.get("/fundlimit")

            # Format the response nicely
            response_text = "Trading Account Fund Information:\n"
            response_text += f"Client ID: {data.get('dhanClientId', 'N/A')}\n"
            response_text += f"Available Balance: ₹{data.get('availabelBalance', 0):.2f}\n"
            response_text += f"Withdrawable Balance: ₹{data.get('withdrawableBalance', 0):.2f}\n"
            response_text += f"SOD Limit: ₹{data.get('sodLimit', 0):.2f}\n"
            response_text += f"Utilized Amount: ₹{data.get('utilizedAmount', 0):.2f}\n"
            response_text += f"Collateral Amount: ₹{data.get('collateralAmount', 0):.2f}\n"
            response_text += f"Receiveable Amount: ₹{data.get('receiveableAmount', 0):.2f}\n"
            response_text += f"Blocked Payout: ₹{data.get('blockedPayoutAmount', 0):.2f}\n"

            # Calculate utilization percentage
            sod_limit = data.get('sodLimit', 0)
            utilized = data.get('utilizedAmount', 0)
            if sod_limit > 0:
                utilization_pct = (utilized / sod_limit) * 100
                response_text += f"Utilization: {utilization_pct:.1f}%"

            return [TextContent(type="text", text=response_text)]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        logger.error(f"Tool execution failed: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point"""
    global config, api_client

    # TODO: Load configuration from environment variables or config file
    # For now, this is a placeholder - user needs to set their access token
    import os
    access_token = os.getenv("DHAN_ACCESS_TOKEN")

    if not access_token:
        logger.error("DHAN_ACCESS_TOKEN environment variable not set")
        print("Please set DHAN_ACCESS_TOKEN environment variable with your Dhan API access token")
        return

    config = DhanConfig(access_token=access_token)
    api_client = DhanAPIClient(config)

    # Run the server
    from mcp.server.stdio import stdio_server
    # from mcp.server.http import http_server

    async with api_client:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )


if __name__ == "__main__":
    asyncio.run(main())