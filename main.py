#!/usr/bin/env python3
"""
CryptoWeather MCP Server
AI-powered Bitcoin price prediction signals
"""

import os
import sys
import argparse
import json
import requests
from datetime import datetime

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as e:
    print(f"Error importing FastMCP: {e}", file=sys.stderr)
    print("Please install FastMCP: pip install fastmcp", file=sys.stderr)
    sys.exit(1)

# Parse command line arguments
parser = argparse.ArgumentParser(description="CryptoWeather MCP Server")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

# Initialize server
mcp = FastMCP("cryptoweather")

# CryptoWeather API endpoint
CRYPTOWEATHER_API_URL = os.getenv("CRYPTOWEATHER_API_URL", "https://cryptoweather.xyz/signal_btc")

@mcp.tool()
def get_bitcoin_signal() -> str:
    """Get current Bitcoin price prediction signal from CryptoWeather AI"""
    try:
        response = requests.get(CRYPTOWEATHER_API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract information from the response
        clear_data = data.get("Clear", {})
        version = data.get("version", "unknown")
        
        # Format the response
        signal_info = {
            "Signal": clear_data.get("signal", "Unknown"),
            "Clarity": clear_data.get("Clarity", "Unknown"),
            "Position": clear_data.get("pos", "Unknown"),
            "Profit": clear_data.get("profit", "Unknown"),
            "Backtest Performance": clear_data.get("backtest", "Unknown"),
            "Signal Code": clear_data.get("sig", "Unknown"),
            "API Version": version,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        result = "🔮 CryptoWeather Bitcoin Signal\n"
        result += "=" * 40 + "\n"
        for key, value in signal_info.items():
            result += f"{key}: {value}\n"
        
        return result
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching Bitcoin signal: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        return f"❌ Error parsing Bitcoin signal: Invalid JSON response - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@mcp.tool()
def get_trading_recommendation() -> str:
    """Get detailed trading recommendation based on current Bitcoin signal"""
    try:
        response = requests.get(CRYPTOWEATHER_API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
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
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching trading recommendation: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        return f"❌ Error parsing trading data: Invalid JSON response - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@mcp.tool()
def get_performance_metrics() -> str:
    """Get CryptoWeather AI performance metrics and statistics"""
    try:
        response = requests.get(CRYPTOWEATHER_API_URL, timeout=10)
        response.raise_for_status()
        
        data = response.json()
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
        
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching performance metrics: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        return f"❌ Error parsing performance data: Invalid JSON response - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

@mcp.tool()
def get_signal_history() -> str:
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
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="CryptoWeather MCP Server")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode")
        args = parser.parse_args()
        
        # Debug output if enabled
        if args.debug:
            print("Starting CryptoWeather MCP Server...", file=sys.stderr)
            print(f"API Endpoint: {CRYPTOWEATHER_API_URL}", file=sys.stderr)
            print(f"Python version: {sys.version}", file=sys.stderr)
            print(f"Working directory: {os.getcwd()}", file=sys.stderr)
        
        # Run the server
        mcp.run()
        
    except Exception as e:
        print(f"Error starting CryptoWeather MCP Server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Main execution
if __name__ == "__main__":
    main()