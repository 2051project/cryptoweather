# CryptoWeather AI Bitcoin prediction Signal Robo-advisor

[![smithery badge](https://smithery.ai/badge/@2051project/cryptoweather)](https://smithery.ai/server/@2051project/cryptoweather)
[![MCP Badge](https://lobehub.com/badge/mcp/2051project-cryptoweather)](https://lobehub.com/mcp/2051project-cryptoweather)

🌈 AI-powered Bitcoin price prediction signals through Model Context Protocol (MCP)

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

Install from source:

```bash
git clone https://github.com/2051project/cryptoweather.git
cd cryptoweather
pip install -e .
```

## Usage
Once installed, you can use the following tools in your Claude conversations:

### Available Tools

Signal tools (CryptoWeather AI):

1. **`get_crypto_signal(asset)`** - Get current prediction signal for `btc`, `eth`, or `ada`
2. **`get_bitcoin_signal()`** - Get current Bitcoin prediction signal
3. **`get_ethereum_signal()`** - Get current Ethereum prediction signal
4. **`get_trading_recommendation(asset)`** - Get detailed trading advice
5. **`get_performance_metrics(asset)`** - View AI performance statistics
6. **`get_signal_history()`** - Learn about signal methodology

Market detail tools (1h market data from the CryptoWeather API — the same indicators the app's detail screen shows):

7. **`get_market_detail(asset)`** - Full technical snapshot: latest OHLCV, 24h change/volume, EMA 9/21/50, RSI(14), Stochastic(14,3,3), MACD(12,26,9)
8. **`get_ohlcv(asset, limit)`** - Recent hourly candles (open, high, low, close, volume)
9. **`get_indicator(asset, indicator, period)`** - A single indicator or price field: `open`, `high`, `low`, `close`, `volume`, `rsi`, `stochastic`, `ema`, `macd`

### Example Usage

![conversations](img/cryptoweatherMCP_chat.gif)

## Signal Types

- **Sunny ☀️**: Strong directional signal with high confidence
- **Cloudy ☁️**: Mixed or uncertain market conditions

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