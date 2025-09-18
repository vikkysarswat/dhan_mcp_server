# Dhan MCP Server

A comprehensive Model Context Protocol (MCP) server for seamless integration with the Dhan trading platform API. This production-ready server provides complete trading functionality, market data access, and portfolio management through the MCP protocol.

## 🚀 Features

### Trading Operations
- **Order Management**: Place, modify, and cancel orders with full lifecycle tracking
- **Order Types**: Market, Limit, Stop Loss, and Stop Loss Market orders
- **Product Types**: CNC, Intraday, Margin, MTF, Cover Order (CO), and Bracket Order (BO)
- **Slice Orders**: Automatic handling of large orders above freeze limits
- **Margin Calculator**: Pre-trade margin requirement calculations

### Market Data
- **Live Prices**: Real-time Last Traded Price (LTP) for multiple instruments
- **OHLC Data**: Open, High, Low, Close with volume information
- **Market Depth**: Full order book with bid/ask levels
- **Historical Data**: Daily and intraday OHLC data with customizable intervals

### Account Management
- **Profile Information**: Complete user profile and account details
- **Fund Limits**: Available balance, margins, and buying power
- **Trade History**: Detailed trade execution records
- **Ledger Reports**: Account statement with credit/debit entries

### Instrument Master
- **Search Instruments**: Find stocks, derivatives, and commodities by name
- **Complete Master**: Access to full instrument database
- **Multiple Exchanges**: Support for NSE, BSE, and MCX segments

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- Dhan trading account with API access
- Valid Dhan API access token

### Quick Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dhan-mcp-server.git
cd dhan-mcp-server
```

2. **Run automated setup**
```bash
python setup.py
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your DHAN_ACCESS_TOKEN
# Edit .env and add you DHAN_CLIENT_ID
```

4. **Start the server**
```bash
# On Linux/macOS
./run_server.sh

# On Windows
run_server.bat
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following:

```env
DHAN_ACCESS_TOKEN=your_dhan_api_access_token_here
DHAN_CLIENT_ID=your_dhan_client_id_here
```

### Claude/MCP Client Setup
Add to your MCP client configuration:

```json
{
    "mcpServers": {
        "dhan-mcp-server": {
            "command": "path/to/your/dhan-mcp-server/run_server.sh",
            "args": []
        }
    }
}
```

## 🛠️ Available Tools

### Account Management
- `get_profile()` - User profile and account information
- `validate_token()` - Access token validation and expiry
- `get_fund_limits()` - Account balance and margin information

### Trading Operations
- `place_order({...})` - Place new orders (all types & products)
- `modify_order({...})` - Modify pending orders
- `cancel_order({orderId})` - Cancel pending orders
- `slice_order({...})` - Handle large quantity orders

### Order & Trade Tracking
- `get_orders()` - Current day's order book
- `get_order_by_id({orderId})` - Specific order details
- `get_order_by_correlation_id({correlationId})` - Find order by custom ID
- `get_trades()` - Current day's executed trades
- `get_trades_by_order_id({orderId})` - Trades for specific order

### Risk Management
- `calculate_margin({...})` - Pre-trade margin calculation

### Market Data
- `get_market_ltp({...})` - Live last traded prices
- `get_market_ohlc({...})` - OHLC data with volume
- `get_market_depth({...})` - Full market depth & order book

### Historical Data
- `get_historical_data({...})` - Daily OHLC historical data
- `get_intraday_data({...})` - Minute-level intraday data

### Reports & Statements
- `get_ledger({from_date, to_date})` - Account ledger reports
- `get_historical_trades({...})` - Historical trade analysis

### Instrument Master Data
- `get_instrument_master({...})` - Complete instrument list
- `search_instruments({query})` - Search instruments by name

## 📋 Usage Examples

### Place a Market Order
```python
# Place a buy order for 100 shares of RELIANCE
place_order({
    "dhanClientId": "your_client_id",
    "transactionType": "BUY",
    "exchangeSegment": "NSE_EQ",
    "productType": "CNC",
    "orderType": "MARKET",
    "validity": "DAY",
    "securityId": "2885",  # RELIANCE security ID
    "quantity": 100
})
```

### Get Market Data
```python
# Get live price for multiple stocks
get_market_ltp({
    "client_id": "your_client_id",
    "instruments": {
        "NSE_EQ": ["2885", "1333"]  # RELIANCE, INFY
    }
})
```

### Calculate Margin
```python
# Check margin requirement before placing order
calculate_margin({
    "dhanClientId": "your_client_id",
    "exchangeSegment": "NSE_EQ",
    "transactionType": "BUY",
    "quantity": 100,
    "productType": "INTRADAY",
    "securityId": "2885",
    "price": 2500
})
```

## 🏗️ Technical Architecture

### Core Components
- **MCP Server**: Full Model Context Protocol implementation
- **API Client**: Async HTTP client with comprehensive error handling
- **Data Models**: 15+ Pydantic models with complete validation
- **Type Safety**: Full enum definitions and input validation
- **Error Handling**: Production-grade API error management

### Security Features
- **Environment Variables**: Secure token storage
- **Input Validation**: Comprehensive Pydantic validation
- **Error Sanitization**: Safe error message handling
- **Rate Limiting**: API rate limit compliance

## 🧪 Development

### Project Structure
```
dhan-mcp-server/
├── dhan_mcp_server/           # Core implementation
│   ├── server.py              # Main MCP server
│   ├── models.py              # Pydantic data models
│   └── utils.py               # Utility functions
├── examples/
│   └── example_usage.py       # Usage examples
├── tests/                     # Test suite
├── setup.py                   # Automated setup
├── run_server.sh/.bat         # Cross-platform scripts
├── pyproject.toml            # Modern Python packaging
├── README.md                 # This file
└── .env.example              # Configuration template
```

### Development Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy dhan_mcp_server/
```

## 🚦 API Coverage

Complete implementation of all major Dhan API endpoints:

| Category | Coverage |
|----------|----------|
| Profile & Authentication | ✅ 100% |
| Orders & Trading | ✅ 100% |
| Market Data | ✅ 100% |
| Historical Data | ✅ 100% |
| Account Information | ✅ 100% |
| Instrument Master | ✅ 100% |

**Total: 22 production-ready tools**

## 🔒 Security & Compliance

- **Token Security**: Environment-based secure storage
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Safe error message sanitization
- **Trading Safety**: Pre-trade risk assessment and validation
- **Audit Trail**: Complete transaction logging

## 📊 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.10
COPY . /app
WORKDIR /app
RUN pip install -e .
CMD ["python", "-m", "dhan_mcp_server.server"]
```

### Systemd Service
```ini
[Unit]
Description=Dhan MCP Server
After=network.target

[Service]
Type=simple
User=dhan
WorkingDirectory=/opt/dhan-mcp-server
Environment=PATH=/opt/dhan-mcp-server/venv/bin
ExecStart=/opt/dhan-mcp-server/venv/bin/python -m dhan_mcp_server.server
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and development purposes. Trading in financial markets involves substantial risk of loss. Users should thoroughly test all functionality in a paper trading environment before using with real capital. The authors are not responsible for any financial losses incurred through the use of this software.

## 📞 Support

- **Documentation**: [API Reference](docs/api.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/dhan-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/dhan-mcp-server/discussions)

## 🔗 Links

- [Dhan API Documentation](https://dhanhq.co/docs/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic Claude](https://www.anthropic.com/claude)

---

**Made with ❤️ for the trading community**
