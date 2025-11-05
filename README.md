# Dhan MCP Server - Python Trading API Integration with Model Context Protocol

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-MCP%20Server-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Dhan API](https://img.shields.io/badge/Dhan-Trading%20API-orange.svg)](https://dhanhq.co/)

**Production-ready MCP server for algorithmic trading with Dhan broker API** - Complete integration with Dhan trading platform providing market data, order management, portfolio tracking, and real-time trading capabilities through the Model Context Protocol.

## 🚀 Overview

The **Dhan MCP Server** is a comprehensive Python-based Model Context Protocol (MCP) server that enables seamless integration with the Dhan trading platform. Ideal for **algorithmic trading**, **automated trading systems**, **trading bots**, and **quantitative trading strategies** in Indian stock markets.

### Key Features

- **Complete Trading Suite**: 19 production-ready tools for order execution, position management, and market analysis
- **Real-time Market Data**: Live LTP, OHLC, market depth, and tick-by-tick data streaming
- **Order Management**: Place, modify, cancel orders with support for all order types (Market, Limit, Stop Loss, Cover, Bracket)
- **Risk Management**: Pre-trade margin calculation and position monitoring
- **Historical Data**: Access to intraday and daily historical data for backtesting
- **Portfolio Tracking**: Real-time positions, holdings, and P&L monitoring
- **MCP Protocol**: Standards-compliant Model Context Protocol implementation using FastMCP

## 📋 Installation

### Prerequisites

- Python 3.8 or higher
- Dhan trading account with API access
- Dhan API credentials (Client ID and Access Token)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/vikkysarswat/dhan-mcp-server.git
cd dhan-mcp-server

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export DHAN_CLIENT_ID="your_client_id"
export DHAN_ACCESS_TOKEN="your_access_token"

# Run the MCP server
python -m dhan_mcp_server
```

### Installation via pip

```bash
pip install dhan-mcp-server
```

### Configuration

Create a `.env` file in the project root:

```env
DHAN_CLIENT_ID=your_dhan_client_id
DHAN_ACCESS_TOKEN=your_dhan_access_token
```

## 📊 Complete Feature Matrix

### **Account Management (3 Tools)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `get_profile()` | User profile and account information | ✅ Complete |
| `validate_token()` | Access token validation and expiry | ✅ Complete |
| `get_fund_limits()` | Account balance and margin information | ✅ Complete |

### **Trading Operations (4 Tools)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `place_order({...})` | Place new orders (all types & products) | ✅ Complete |
| `modify_order({...})` | Modify pending orders | ✅ Complete |
| `cancel_order({orderId})` | Cancel pending orders | ✅ Complete |
| `slice_order({...})` | Handle large quantity orders | ✅ Complete |

### **Order & Trade Tracking (5 Tools)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `get_orders()` | Current day's order book | ✅ Complete |
| `get_order_by_id({orderId})` | Specific order details | ✅ Complete |
| `get_order_by_correlation_id({correlationId})` | Find order by custom ID | ✅ Complete |
| `get_trades()` | Current day's executed trades | ✅ Complete |
| `get_trades_by_order_id({orderId})` | Trades for specific order | ✅ Complete |

### **Position & Holdings Management (2 Tools)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `get_positions()` | Real-time open positions | ✅ Complete |
| `get_holdings()` | Long-term holdings portfolio | ✅ Complete |

### **Risk Management (1 Tool)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `calculate_margin({...})` | Pre-trade margin calculation | ✅ Complete |

### **Market Data (3 Tools)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `get_market_ltp({...})` | Live last traded prices | ✅ Complete |
| `get_market_ohlc({...})` | OHLC data with volume | ✅ Complete |
| `get_market_depth({...})` | Full market depth & order book | ✅ Complete |

### **Historical Data & Analysis (3 Tools)**

| Tool | Functionality | Status |
|------|---------------|--------|
| `get_historical_data({...})` | Daily OHLC historical data | ✅ Complete |
| `get_intraday_data({...})` | Minute-level intraday data | ✅ Complete |
| `get_tick_data({...})` | Tick-by-tick historical data | ✅ Complete |

## 🔧 Usage Examples

### Place a Market Order

```python
from dhan_mcp_server import DhanMCPServer

server = DhanMCPServer()
order = server.place_order(
    security_id="1333",  # Reliance
    exchange="NSE",
    transaction_type="BUY",
    quantity=1,
    order_type="MARKET",
    product_type="INTRADAY"
)
```

### Get Real-time Market Data

```python
# Get LTP for multiple securities
ltp_data = server.get_market_ltp(
    exchange="NSE",
    security_ids=["1333", "11536"]  # Reliance, TCS
)

# Get market depth
depth = server.get_market_depth(
    exchange="NSE",
    security_id="1333"
)
```

### Retrieve Historical Data

```python
import datetime

historical = server.get_historical_data(
    security_id="1333",
    exchange="NSE",
    instrument="EQUITY",
    from_date=datetime.date(2024, 1, 1),
    to_date=datetime.date(2024, 12, 31)
)
```

## 🏗️ Architecture

Built with:
- **FastMCP**: High-performance MCP server framework
- **Dhan Python SDK**: Official Dhan trading API client
- **Python AsyncIO**: Asynchronous operations for real-time data

## 🔐 Security

- Never commit API credentials to version control
- Use environment variables or secure vaults for sensitive data
- Implement IP whitelisting on Dhan platform
- Enable 2FA on your Dhan account

## 📝 API Documentation

For detailed Dhan API documentation, visit:
- [Dhan API Documentation](https://dhanhq.co/docs/)
- [Dhan Python SDK](https://github.com/dhan-oss/DhanHQ-py)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io/) - Protocol specification
- [Dhan Trading Platform](https://dhanhq.co/) - Trading broker

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Keywords

algorithmic trading, trading bot, stock market API, Dhan API, MCP server, Model Context Protocol, Python trading, automated trading, quantitative trading, Indian stock market, NSE, BSE, equity trading, derivatives trading, market data API, real-time trading, trading automation, backtesting, trading strategy
