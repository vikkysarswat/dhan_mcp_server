#!/usr/bin/env python3
"""
Example usage of Dhan MCP Server
This file demonstrates how to use the various tools and resources provided by the server.
"""

import asyncio
import os
from dhan_mcp_server.server import DhanAPIClient, DhanConfig


async def example_usage():
    """Demonstrate various Dhan API operations"""

    # Get access token from environment
    access_token = os.getenv("DHAN_ACCESS_TOKEN")
    if not access_token:
        print("Please set DHAN_ACCESS_TOKEN environment variable")
        return

    # Initialize configuration and API client
    config = DhanConfig(access_token=access_token)

    async with DhanAPIClient(config) as client:
        try:
            # 1. Get user profile
            print("=== User Profile ===")
            profile = await client.get("/profile")
            print(f"Client ID: {profile.get('dhanClientId')}")
            print(f"Token Valid Until: {profile.get('tokenValidity')}")
            print(f"Active Segments: {profile.get('activeSegment')}")
            print()

            # 2. Get orders for the day
            print("=== Today's Orders ===")
            orders = await client.get("/orders")
            if isinstance(orders, list):
                print(f"Total orders: {len(orders)}")
                for order in orders[:3]:  # Show first 3 orders
                    print(f"Order ID: {order.get('orderId')}")
                    print(f"Symbol: {order.get('tradingSymbol', 'N/A')}")
                    print(f"Status: {order.get('orderStatus')}")
                    print(
                        f"Type: {order.get('transactionType')} {order.get('quantity')} @ {order.get('price', 'Market')}")
                    print("---")
            else:
                print("No orders found")
            print()

            # 3. Get trades for the day
            print("=== Today's Trades ===")
            trades = await client.get("/trades")
            if isinstance(trades, list):
                print(f"Total trades: {len(trades)}")
                total_value = 0
                for trade in trades[:3]:  # Show first 3 trades
                    trade_value = trade.get('tradedQuantity', 0) * trade.get('tradedPrice', 0)
                    total_value += trade_value
                    print(f"Order ID: {trade.get('orderId')}")
                    print(f"Symbol: {trade.get('tradingSymbol', 'N/A')}")
                    print(
                        f"Trade: {trade.get('transactionType')} {trade.get('tradedQuantity')} @ ₹{trade.get('tradedPrice')}")
                    print(f"Value: ₹{trade_value:.2f}")
                    print("---")
                print(f"Sample total value: ₹{total_value:.2f}")
            else:
                print("No trades found")
            print()

            # 4. Get fund limits and account information
            print("=== Account Funds ===")
            funds = await client.get("/fundlimit")
            print(f"Client ID: {funds.get('dhanClientId')}")
            print(f"Available Balance: ₹{funds.get('availabelBalance', 0):,.2f}")
            print(f"Withdrawable Balance: ₹{funds.get('withdrawableBalance', 0):,.2f}")
            print(f"SOD Limit: ₹{funds.get('sodLimit', 0):,.2f}")
            print(f"Utilized Amount: ₹{funds.get('utilizedAmount', 0):,.2f}")

            # Calculate utilization percentage
            sod_limit = funds.get('sodLimit', 0)
            utilized = funds.get('utilizedAmount', 0)
            if sod_limit > 0:
                utilization_pct = (utilized / sod_limit) * 100
                print(f"Utilization: {utilization_pct:.1f}%")
            print()

            # 5. Calculate margin for a sample order
            print("=== Margin Calculator Example ===")
            margin_request = {
                "dhanClientId": profile.get('dhanClientId'),
                "exchangeSegment": "NSE_EQ",
                "transactionType": "BUY",
                "quantity": 1,
                "productType": "INTRADAY",
                "securityId": "11536",  # TCS
                "price": 3000.0,
                "triggerPrice": 0
            }

            margin_result = await client.post("/margincalculator", margin_request)
            print("Sample Margin Calculation (TCS - 1 share @ ₹3000):")
            print(f"Total Margin Required: ₹{margin_result.get('totalMargin', 0):.2f}")
            print(f"Available Balance: ₹{margin_result.get('availableBalance', 0):.2f}")
            print(f"Span Margin: ₹{margin_result.get('spanMargin', 0):.2f}")
            print(f"Exposure Margin: ₹{margin_result.get('exposureMargin', 0):.2f}")
            print(f"Brokerage: ₹{margin_result.get('brokerage', 0):.2f}")
            print(f"Leverage: {margin_result.get('leverage', 'N/A')}x")

            insufficient = margin_result.get('insufficientBalance', 0)
            if insufficient > 0:
                print(f"⚠️ Insufficient Balance: ₹{insufficient:.2f}")
            else:
                print("✅ Sufficient balance available")
            print()

            # 6. Market data example
            print("=== Market Data Example ===")
            try:
                # Get LTP for TCS (NSE_EQ: 11536)
                instruments = {"NSE_EQ": ["11536"]}

                # Note: This requires client-id header
                headers = {"client-id": profile.get('dhanClientId')}
                response = await client.session.post(
                    "/marketfeed/ltp",
                    json={"NSE_EQ": [11536]},
                    headers={**client.session.headers, **headers}
                )

                if response.status_code == 200:
                    market_data = response.json()
                    if market_data.get("status") == "success":
                        tcs_data = market_data["data"]["NSE_EQ"]["11536"]
                        print(f"TCS LTP: ₹{tcs_data['last_price']}")
                    else:
                        print("Market data request failed")
                else:
                    print(f"Market data API returned: {response.status_code}")
            except Exception as e:
                print(f"Market data example skipped: {e}")
            print()

            # 7. Historical data example
            print("=== Historical Data Example ===")
            try:
                historical_request = {
                    "securityId": "11536",  # TCS
                    "exchangeSegment": "NSE_EQ",
                    "instrument": "EQUITY",
                    "expiryCode": 0,
                    "oi": False,
                    "fromDate": "2024-01-01",
                    "toDate": "2024-01-10"
                }

                historical_data = await client.post("/charts/historical", historical_request)
                if "open" in historical_data and len(historical_data["open"]) > 0:
                    print(f"Historical data points: {len(historical_data['open'])}")
                    print(
                        f"Latest OHLC: O:{historical_data['open'][-1]} H:{historical_data['high'][-1]} L:{historical_data['low'][-1]} C:{historical_data['close'][-1]}")
                else:
                    print("No historical data returned")
            except Exception as e:
                print(f"Historical data example skipped: {e}")
            print()

            # 8. Example order placement (COMMENTED OUT FOR SAFETY)
            # UNCOMMENT AND MODIFY CAREFULLY FOR ACTUAL TRADING
            """
            print("=== Example Order Placement ===")
            order_data = {
                "dhanClientId": profile.get('dhanClientId'),
                "correlationId": "example_order_001",
                "transactionType": "BUY",
                "exchangeSegment": "NSE_EQ",
                "productType": "INTRADAY",
                "orderType": "LIMIT",
                "validity": "DAY",
                "securityId": "11536",  # TCS security ID
                "quantity": "1",
                "price": "3000.00",
                "disclosedQuantity": "",
                "triggerPrice": "",
                "afterMarketOrder": False,
                "amoTime": "",
                "boProfitValue": "",
                "boStopLossValue": ""
            }

            # CAUTION: This will place a real order!
            # order_response = await client.post("/orders", order_data)
            # print(f"Order placed: {order_response}")
            """

        except Exception as e:
            print(f"Error: {e}")


def example_mcp_client_usage():
    """Example of how to use the MCP server from a client perspective"""
    print("""
=== MCP Server Usage Example ===

1. Start the MCP server:
   export DHAN_ACCESS_TOKEN="your-token-here"
   uv run python server.py

2. Available Resources:
   - dhan://profile - User profile information
   - dhan://orders - Today's orders
   - dhan://trades - Today's trades
   - dhan://positions - Current positions (when implemented)
   - dhan://holdings - Long-term holdings (when implemented)
   - dhan://funds - Account funds (when implemented)

3. Available Tools:
   - get_profile() - Get user profile
   - validate_token() - Check token validity
   - place_order(...) - Place a new order
   - modify_order(...) - Modify pending order
   - cancel_order(orderId) - Cancel pending order
   - slice_order(...) - Place sliced orders
   - get_orders() - Get all orders for today
   - get_order_by_id(orderId) - Get specific order details
   - get_order_by_correlation_id(correlationId) - Get order by correlation ID
   - get_trades() - Get all trades for today
   - get_trades_by_order_id(orderId) - Get trades for specific order

4. Example Tool Calls:

   # Get profile
   get_profile()

   # Place a buy order
   place_order({
       "dhanClientId": "your-client-id",
       "transactionType": "BUY",
       "exchangeSegment": "NSE_EQ",
       "productType": "INTRADAY",
       "orderType": "LIMIT",
       "validity": "DAY",
       "securityId": "11536",
       "quantity": 1,
       "price": 3000.00
   })

   # Calculate margin before placing an order
   calculate_margin({
       "dhanClientId": "your-client-id",
       "exchangeSegment": "NSE_EQ",
       "transactionType": "BUY",
       "quantity": 1,
       "productType": "INTRADAY",
       "securityId": "11536",
       "price": 3000.0
   })

   # Get fund limits and account information
   get_fund_limits()

   # Cancel an order
   cancel_order({"orderId": "112111182198"})

   # Get order status
   get_order_by_id({"orderId": "112111182198"})

5. Error Handling:
   All tools return proper error messages for:
   - Invalid parameters
   - API rate limit exceeded
   - Network errors
   - Authentication failures
   - Order rejection reasons
""")


if __name__ == "__main__":
    print("Dhan MCP Server Example Usage")
    print("=" * 40)

    # Show MCP usage examples
    example_mcp_client_usage()

    # Run API examples if token is available
    if os.getenv("DHAN_ACCESS_TOKEN"):
        print("\n" + "=" * 40)
        print("Running API Examples...")
        asyncio.run(example_usage())
    else:
        print("\nTo run API examples, set DHAN_ACCESS_TOKEN environment variable")