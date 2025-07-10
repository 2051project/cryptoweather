#!/usr/bin/env python3
import os
import sys
import argparse
import json
import requests
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# CryptoWeather API endpoint
CRYPTOWEATHER_API_URL = os.getenv("CRYPTOWEATHER_API_URL", "https://cryptoweather.xyz/signal_btc")

# Initialize server
mcp = FastMCP("cryptoweather")

def fetch_bitcoin_signal():
    """Helper function to fetch Bitcoin signal from CryptoWeather API"""
    try:
        response = requests.get(CRYPTOWEATHER_API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")

@mcp.tool()
def get_bitcoin_signal() -> str:
    """Get current Bitcoin price prediction signal from CryptoWeather AI"""
    try:
        data = fetch_bitcoin_signal()
        
        # Extract information from the response
        clear_data = data.get("Clear", {})
        version = data.get("version", "unknown")
        
        # Format the response
        result = "🔮 CryptoWeather Bitcoin Signal\n"
        result += "=" * 40 + "\n"
        result += f"Signal: {clear_data.get('signal', 'Unknown')}\n"
        result += f"Clarity: {clear_data.get('Clarity', 'Unknown')}\n"
        result += f"Position: {clear_data.get('pos', 'Unknown')}\n"
        result += f"Profit: {clear_data.get('profit', 'Unknown')}\n"
        result += f"Backtest Performance: {clear_data.get('backtest', 'Unknown')}\n"
        result += f"Signal Code: {clear_data.get('sig', 'Unknown')}\n"
        result += f"API Version: {version}\n"
        result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error fetching Bitcoin signal: {str(e)}"

@mcp.tool()
def get_trading_recommendation() -> str:
    """Get detailed trading recommendation based on current Bitcoin signal"""
    try:
        data = fetch_bitcoin_signal()
        clear_data = data.get("Clear", {})
        
        position = clear_data.get("pos", "").lower()
        signal = clear_data.get("signal", "")
        clarity = clear_data.get("Clarity", "0%")
        profit = clear_data.get("profit", "0%")
        
        # Generate recommendation based on position
        if position == "buy":
            recommendation = "🟢 BUY SIGNAL"
            action = "Consider opening a long position"
        elif position == "sell":
            recommendation = "🔴 SELL SIGNAL"
            action = "Consider opening a short position or closing long positions"
        elif position == "hold":
            recommendation = "🟡 HOLD SIGNAL"
            action = "Maintain current position, wait for clearer signals"
        else:
            recommendation = "⚪ UNKNOWN SIGNAL"
            action = "Exercise caution, signal unclear"
        
        result = f"📊 Bitcoin Trading Recommendation\n"
        result += "=" * 40 + "\n"
        result += f"Current Signal: {signal}\n"
        result += f"Recommendation: {recommendation}\n"
        result += f"Action: {action}\n"
        result += f"Signal Clarity: {clarity}\n"
        result += f"Current Profit: {profit}\n"
        result += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        result += "⚠️ Disclaimer: This is AI-generated prediction for informational purposes only. "
        result += "Always do your own research and consider your risk tolerance before trading."
        
        return result
        
    except Exception as e:
        return f"❌ Error fetching trading recommendation: {str(e)}"

@mcp.tool()
def get_performance_metrics() -> str:
    """Get CryptoWeather AI performance metrics and statistics"""
    try:
        data = fetch_bitcoin_signal()
        clear_data = data.get("Clear", {})
        
        backtest = clear_data.get("backtest", "0%")
        profit = clear_data.get("profit", "0%")
        clarity = clear_data.get("Clarity", "0%")
        
        result = f"📈 CryptoWeather Performance Metrics\n"
        result += "=" * 40 + "\n"
        result += f"Backtest Performance: {backtest}\n"
        result += f"Current Profit: {profit}\n"
        result += f"Signal Clarity: {clarity}\n"
        result += f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        result += "📝 Performance Notes:\n"
        result += f"• Backtest shows historical performance of {backtest}\n"
        result += f"• Current cycle profit is {profit}\n"
        result += f"• Signal clarity indicates {clarity} confidence level\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error fetching performance metrics: {str(e)}"

@mcp.tool()
def get_signal_information() -> str:
    """Get information about CryptoWeather signal updates and methodology"""
    return """🕐 CryptoWeather Signal Information
========================================
Update Frequency: Every hour
Signal Types: Clear, Cloudy, Stormy weather indicators
Position Types: Buy, Sell, Hold

📊 How to Interpret Signals:
• Clear ☀️: Strong directional signal
• Cloudy ☁️: Mixed or uncertain conditions  
• Stormy ⛈️: High volatility expected

🎯 Position Meanings:
• Buy: AI predicts price increase
• Sell: AI predicts price decrease
• Hold: AI suggests maintaining current position

⚡ Signal Updates:
Signals are updated every hour based on:
- Market sentiment analysis
- Technical indicators
- AI pattern recognition
- Historical backtesting

🔍 Clarity Percentage:
Higher clarity indicates stronger confidence in the signal.
Generally, clarity above 70% suggests higher reliability.

⚠️ Important Notes:
- Past performance doesn't guarantee future results
- Use signals as part of broader analysis
- Always manage risk appropriately
- Consider multiple timeframes and indicators"""

def main():
    """Main entry point for the MCP server"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CryptoWeather MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()
    
    # Debug output if enabled
    if args.debug:
        print("Starting CryptoWeather MCP Server...", file=sys.stderr)
        print(f"API Endpoint: {CRYPTOWEATHER_API_URL}", file=sys.stderr)
        print("Registered tools:", file=sys.stderr)
        print("  - get_bitcoin_signal", file=sys.stderr)
        print("  - get_trading_recommendation", file=sys.stderr)
        print("  - get_performance_metrics", file=sys.stderr)
        print("  - get_signal_information", file=sys.stderr)
    
    # Run the server
    mcp.run()

# Main execution
if __name__ == "__main__":
    main()