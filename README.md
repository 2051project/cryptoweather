# CryptoWeather MCP Server

🔮 AI-powered Bitcoin price prediction signals through Model Context Protocol (MCP)

## Overview

CryptoWeather MCP Server provides real-time Bitcoin price prediction signals from the CryptoWeather AI system. Get hourly updated trading signals, performance metrics, and AI-driven market insights directly in your Claude conversations.

## Features

- **Real-time Bitcoin Signals**: Get current AI predictions for Bitcoin price movements
- **Trading Recommendations**: Receive detailed buy/sell/hold recommendations
- **Performance Metrics**: Access historical backtest results and current profit metrics
- **Signal Analysis**: Understand signal clarity and confidence levels
- **Hourly Updates**: Fresh predictions updated every hour

## Installation

### For Claude Desktop Users

1. Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "cryptoweather": {
      "command": "python",
      "args": ["/path/to/cryptoweather/main.py"]
    }
  }
}
```

### For Developers

```bash
pip install cryptoweather
```

Or install from source:

```bash
git clone https://github.com/2051project/cryptoweather.git
cd cryptoweather
pip install -e .
```

## Usage

Once installed, you can use the following tools in your Claude conversations:

### Available Tools

1. **`get_bitcoin_signal()`** - Get current Bitcoin prediction signal
2. **`get_trading_recommendation()`** - Get detailed trading advice
3. **`get_performance_metrics()`** - View AI performance statistics
4. **`get_signal_history()`** - Learn about signal methodology

### Example Usage

```
User: What's the current Bitcoin signal?
Claude: [Uses get_bitcoin_signal() to fetch real-time data]

User: Should I buy Bitcoin right now?
Claude: [Uses get_trading_recommendation() for detailed analysis]

User: How well has the AI performed historically?
Claude: [Uses get_performance_metrics() to show backtest results]
```

## Signal Types

- **☀️ Clear**: Strong directional signal with high confidence
- **☁️ Cloudy**: Mixed or uncertain market conditions
- **⛈️ Stormy**: High volatility expected

## Position Types

- **Buy**: AI predicts price increase
- **Sell**: AI predicts price decrease  
- **Hold**: AI suggests maintaining current position

## API Information

- **Update Frequency**: Every hour
- **Response Format**: JSON with signal, clarity, position, and profit data

## Example Response

```json
{
  "Clear": {
    "Clarity": "74%",
    "backtest": "24,510%",
    "pos": "hold",
    "profit": "538%",
    "sig": "C",
    "signal": "Cloudy ☁️"
  },
  "version": "2.0"
}
```

## Disclaimer

⚠️ **Important**: CryptoWeather predictions are for informational purposes only. This is not financial advice. Always do your own research and consider your risk tolerance before making trading decisions. Past performance does not guarantee future results.

## Support

- Website: [https://cryptoweather.xyz](https://cryptoweather.xyz)
- Issues: [GitHub Issues](https://github.com/2051project/cryptoweather/issues)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Development

### Running in Debug Mode

```bash
python main.py --debug
```

### Requirements

- Python 3.10+
- fastmcp >= 0.1.0
- requests >= 2.28.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

Made with ❤️ by the CryptoWeather Team