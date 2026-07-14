#!/usr/bin/env python3
import os
import sys
import argparse
import json
import requests
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

# Parse command line arguments
parser = argparse.ArgumentParser(description="CryptoWeather MCP Server")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args, _ = parser.parse_known_args()

# PaaS(PlayMCP in KC, Render 등)는 PORT를 주입한다.
# PORT/RENDER가 있으면 Streamable HTTP, 없으면 로컬 클라이언트용 stdio로 뜬다.
PORT = int(os.getenv("PORT", "8000"))

# Initialize server
mcp = FastMCP(
    "cryptoweather",
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
    json_response=True,
)

# CryptoWeather API endpoints
CRYPTOWEATHER_BASE_URL = os.getenv("CRYPTOWEATHER_BASE_URL", "https://cryptoweather.xyz")

ASSETS = {
    "btc": {"title": "Bitcoin", "signal_path": "signal_btc"},
    "eth": {"title": "Ethereum", "signal_path": "signal_eth"},
    "ada": {"title": "ADA", "signal_path": "signal_ada"},
}

ASSET_ALIASES = {
    "bitcoin": "btc", "btcusdt": "btc",
    "ethereum": "eth", "ether": "eth", "ethusdt": "eth",
    "cardano": "ada", "adausdt": "ada",
}


def _resolve_asset(asset: str) -> str:
    key = (asset or "btc").strip().lower()
    key = ASSET_ALIASES.get(key, key)
    if key not in ASSETS:
        raise ValueError(
            f"Unknown asset '{asset}'. Supported: btc (Bitcoin), eth (Ethereum), ada (Cardano)"
        )
    return key


def _signal_url(asset_key: str) -> str:
    # 기존 배포 호환: CRYPTOWEATHER_API_URL이 지정돼 있으면 btc는 그 주소를 그대로 쓴다
    legacy = os.getenv("CRYPTOWEATHER_API_URL")
    if asset_key == "btc" and legacy:
        return legacy
    return f"{CRYPTOWEATHER_BASE_URL}/{ASSETS[asset_key]['signal_path']}"


def _fetch_signal(asset_key: str) -> tuple:
    """Returns (clear_dict, version) from the CryptoWeather signal API.

    eth/ada 응답은 키에 접미사가 붙는다 (signal_eth, pos_eth …) — btc 형태로 정규화.
    """
    response = requests.get(_signal_url(asset_key), timeout=10)
    response.raise_for_status()
    data = response.json()
    clear = data.get("Clear", {})
    suffix = f"_{asset_key}"
    normalized = {
        (k[: -len(suffix)] if k.endswith(suffix) else k): (
            v.strip() if isinstance(v, str) else v
        )
        for k, v in clear.items()
    }
    return normalized, data.get("version", "unknown")


def _fetch_market(asset_key: str, limit: int = 24,
                  rsi_period: int = None, ema_period: int = None) -> dict:
    """CryptoWeather market/indicator API — OHLCV와 지표는 서버가 계산해 내려준다."""
    params = {"asset": asset_key, "limit": limit}
    if rsi_period:
        params["rsi_period"] = rsi_period
    if ema_period:
        params["ema_period"] = ema_period
    response = requests.get(
        f"{CRYPTOWEATHER_BASE_URL}/indicators", params=params, timeout=12
    )
    if response.status_code == 400:
        raise ValueError(response.json().get("error", "Bad request"))
    response.raise_for_status()
    return response.json()


def _fmt(value, digits: int = None) -> str:
    """가격 크기에 따라 소수 자릿수를 조절 (BTC 6만 vs ADA 0.5)."""
    if value is None:
        return "N/A"
    if digits is None:
        a = abs(value)
        digits = 2 if a >= 100 else 4 if a >= 1 else 6
    return f"{value:,.{digits}f}"


def _rsi_label(value) -> str:
    if value is None:
        return "N/A"
    if value >= 70:
        return "Overbought ⚠️"
    if value <= 30:
        return "Oversold ⚠️"
    return "Neutral"


def _stoch_label(k, d) -> str:
    if k is None or d is None:
        return "N/A"
    zone = "Overbought ⚠️" if k >= 80 else "Oversold ⚠️" if k <= 20 else "Neutral"
    cross = "%K > %D (bullish)" if k > d else "%K < %D (bearish)" if k < d else "%K = %D"
    return f"{zone}, {cross}"


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "cryptoweather-mcp"})


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    # 일부 플랫폼(PlayMCP in KC 등)은 컨테이너 포트의 GET / 로 헬스체크한다
    return JSONResponse({"status": "ok", "service": "cryptoweather-mcp", "mcp": "/mcp"})


def _format_signal(asset_key: str) -> str:
    clear_data, version = _fetch_signal(asset_key)
    title = ASSETS[asset_key]["title"]

    signal_info = {
        "Signal": clear_data.get("signal", "Unknown"),
        "Clarity": clear_data.get("Clarity", "Unknown"),
        "Position": clear_data.get("pos", "Unknown"),
        "Profit": clear_data.get("profit", "Unknown"),
        "Backtest Performance": clear_data.get("backtest", "Unknown"),
        "Signal Code": clear_data.get("sig", "Unknown"),
        "API Version": version,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    result = f"🔮 CryptoWeather {title} Signal\n"
    result += "=" * 40 + "\n"
    for key, value in signal_info.items():
        result += f"{key}: {value}\n"
    return result


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Signal",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def get_crypto_signal(asset: str = "btc") -> str:
    """크립토웨더(CryptoWeather) AI의 현재 암호화폐 가격 예측 시그널(날씨)을 조회합니다.

    Args:
        asset: Which coin to check — "btc" (Bitcoin), "eth" (Ethereum), or "ada" (Cardano)
    """
    try:
        return _format_signal(_resolve_asset(asset))
    except ValueError as e:
        return f"❌ {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching signal: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        return f"❌ Error parsing signal: Invalid JSON response - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Bitcoin Signal",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def get_bitcoin_signal() -> str:
    """크립토웨더(CryptoWeather) AI의 현재 비트코인(Bitcoin) 가격 예측 시그널을 조회합니다.
    (get_crypto_signal에서 asset="btc"인 경우와 동일)"""
    return await get_crypto_signal("btc")


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Ethereum Signal",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def get_ethereum_signal() -> str:
    """크립토웨더(CryptoWeather) AI의 현재 이더리움(Ethereum) 가격 예측 시그널을 조회합니다.
    (get_crypto_signal에서 asset="eth"인 경우와 동일)"""
    return await get_crypto_signal("eth")


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Trading Recommendation",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
async def get_trading_recommendation(asset: str = "btc") -> str:
    """크립토웨더(CryptoWeather)의 현재 시그널을 바탕으로 상세 트레이딩 추천 정보를 제공합니다.

    Args:
        asset: Which coin to check — "btc" (Bitcoin), "eth" (Ethereum), or "ada" (Cardano)
    """
    try:
        asset_key = _resolve_asset(asset)
        clear_data, _ = _fetch_signal(asset_key)
        title = ASSETS[asset_key]["title"]

        position = clear_data.get("pos", "").lower()
        signal = clear_data.get("signal", "")
        clarity = clear_data.get("Clarity", "0%")
        profit = clear_data.get("profit", "0%")

        # Generate recommendation based on position
        # (eth는 "🟡 wait"처럼 이모지가 섞여 오므로 부분 일치로 판별)
        if "buy" in position:
            recommendation = "🟢 BUY SIGNAL"
            action = "Consider opening a long position"
        elif "sell" in position:
            recommendation = "🔴 SELL SIGNAL"
            action = "Consider opening a short position or closing long positions"
        elif "hold" in position or "wait" in position:
            recommendation = "🟡 HOLD SIGNAL"
            action = "Maintain current position, wait for clearer signals"
        else:
            recommendation = "⚪ UNKNOWN SIGNAL"
            action = "Exercise caution, signal unclear"

        result = f"📊 {title} Trading Recommendation\n"
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

    except ValueError as e:
        return f"❌ {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching trading recommendation: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        return f"❌ Error parsing trading data: Invalid JSON response - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Performance Metrics",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
def get_performance_metrics(asset: str = "btc") -> str:
    """크립토웨더(CryptoWeather) AI의 성과 지표와 통계(백테스트, 수익률, 신뢰도)를 조회합니다.

    Args:
        asset: Which coin to check — "btc" (Bitcoin), "eth" (Ethereum), or "ada" (Cardano)
    """
    try:
        asset_key = _resolve_asset(asset)
        clear_data, _ = _fetch_signal(asset_key)
        title = ASSETS[asset_key]["title"]

        backtest = clear_data.get("backtest", "0%")
        profit = clear_data.get("profit", "0%")
        clarity = clear_data.get("Clarity", "0%")

        result = f"📈 CryptoWeather {title} Performance Metrics\n"
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

    except ValueError as e:
        return f"❌ {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching performance metrics: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        return f"❌ Error parsing performance data: Invalid JSON response - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Market Detail",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
def get_market_detail(asset: str = "btc") -> str:
    """크립토웨더(CryptoWeather) 1시간봉 시장 데이터 기반의 현재 시장 상세 정보와
    기술적 지표(AI가 참고하는 지표)를 조회합니다: 최신 OHLCV 캔들, 24시간 변동/거래량,
    EMA 9/21/50, RSI(14), Stochastic(14,3,3), MACD(12,26,9).

    Args:
        asset: Which coin to check — "btc" (Bitcoin), "eth" (Ethereum), or "ada" (Cardano)
    """
    try:
        m = _fetch_market(_resolve_asset(asset), limit=1)

        ema_ = m.get("ema", {})
        rsi_ = m.get("rsi", {})
        stoch = m.get("stochastic", {})
        macd_ = m.get("macd", {})

        ema50 = ema_.get("50")
        trend = "above" if ema50 is None or m["close"] >= ema50 else "below"
        hist = macd_.get("histogram") or 0
        macd_state = "bullish (MACD > Signal)" if hist > 0 else "bearish (MACD < Signal)"
        change = m.get("change_24h")

        result = f"📊 {m['title']} ({m['symbol']}) Market Detail — {m['interval']} candles\n"
        result += "=" * 40 + "\n"
        result += f"Candle Time: {m['candle_time']} UTC (latest, in progress)\n\n"
        result += "💰 Price (latest candle)\n"
        result += f"Open:   {_fmt(m['open'])}\n"
        result += f"High:   {_fmt(m['high'])}\n"
        result += f"Low:    {_fmt(m['low'])}\n"
        result += f"Close:  {_fmt(m['close'])}\n"
        result += f"Volume: {_fmt(m['volume'])}\n"
        result += f"24h Change: {change:+.2f}%\n" if change is not None else ""
        result += f"24h Volume: {_fmt(m.get('volume_24h'))}\n\n"
        result += "📈 Technical Indicators\n"
        result += f"EMA9:  {_fmt(ema_.get('9'))}\n"
        result += f"EMA21: {_fmt(ema_.get('21'))}\n"
        result += f"EMA50: {_fmt(ema50)} (price is {trend} EMA50)\n"
        result += f"RSI({rsi_.get('period', 14)}): {_fmt(rsi_.get('value'), 2)} — {_rsi_label(rsi_.get('value'))}\n"
        result += f"Stochastic(14,3,3): %K {_fmt(stoch.get('k'), 2)} / %D {_fmt(stoch.get('d'), 2)} — {_stoch_label(stoch.get('k'), stoch.get('d'))}\n"
        result += f"MACD(12,26,9): {_fmt(macd_.get('line'))} / Signal {_fmt(macd_.get('signal'))} / Hist {_fmt(macd_.get('histogram'))} — {macd_state}\n"

        return result

    except ValueError as e:
        return f"❌ {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching market detail: Network error - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather OHLCV Candles",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
def get_ohlcv(asset: str = "btc", limit: int = 24) -> str:
    """크립토웨더(CryptoWeather)에서 최근 1시간봉 OHLCV 캔들(시가, 고가, 저가, 종가, 거래량)을 조회합니다.

    Args:
        asset: Which coin to check — "btc" (Bitcoin), "eth" (Ethereum), or "ada" (Cardano)
        limit: Number of most recent hourly candles to return (1-200, default 24)
    """
    try:
        limit = max(1, min(int(limit), 200))
        m = _fetch_market(_resolve_asset(asset), limit=limit)
        candles = m.get("candles", [])

        result = f"🕐 {m['title']} ({m['symbol']}) — last {len(candles)} × {m['interval']} candles (UTC)\n"
        result += "=" * 40 + "\n"
        result += f"{'Time':<17}{'Open':>12}{'High':>12}{'Low':>12}{'Close':>12}{'Volume':>14}\n"
        for c in candles:
            result += (
                f"{c['time']:<17}"
                f"{_fmt(c['open']):>12}{_fmt(c['high']):>12}{_fmt(c['low']):>12}"
                f"{_fmt(c['close']):>12}{_fmt(c['volume']):>14}\n"
            )
        result += "\n(The last row is the current, still-forming candle.)"
        return result

    except ValueError as e:
        return f"❌ {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching OHLCV: Network error - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Technical Indicator",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    )
)
def get_indicator(asset: str = "btc", indicator: str = "rsi", period: int = 0) -> str:
    """크립토웨더(CryptoWeather) 1시간봉 시장 데이터에서 단일 기술적 지표 또는 가격 필드를 조회합니다.

    Args:
        asset: Which coin to check — "btc" (Bitcoin), "eth" (Ethereum), or "ada" (Cardano)
        indicator: One of "open", "high", "low", "close" (or "price"), "volume",
                   "rsi", "stochastic", "ema", "macd"
        period: Optional period override for "rsi" (default 14) or "ema"
                (default shows 9/21/50). Ignored for other indicators.
    """
    try:
        asset_key = _resolve_asset(asset)
        name = (indicator or "").strip().lower().replace("%", "").replace(" ", "")
        if name == "price":
            name = "close"

        valid = ("open", "high", "low", "close", "volume",
                 "rsi", "stochastic", "stoch", "stochasticoscillator", "ema", "macd")
        if name not in valid:
            return (
                f"❌ Unknown indicator '{indicator}'. Supported: open, high, low, close, "
                "volume, rsi, stochastic, ema, macd"
            )

        m = _fetch_market(
            asset_key,
            limit=6,
            rsi_period=period if name == "rsi" and period > 1 else None,
            ema_period=period if name == "ema" and period > 1 else None,
        )

        header = f"📐 {m['title']} ({m['symbol']}) — {m['interval']} candles\n" + "=" * 40 + "\n"
        header += f"Candle Time: {m['candle_time']} UTC (latest, in progress)\n"

        if name in ("open", "high", "low", "close", "volume"):
            recent = "  ".join(_fmt(c[name]) for c in m.get("candles", []))
            return (
                header
                + f"{name.capitalize()}: {_fmt(m[name])}\n"
                + f"Last 6 hourly values (oldest→newest): {recent}"
            )

        if name == "rsi":
            rsi_ = m.get("rsi", {})
            value = rsi_.get("value")
            recent = "  ".join(_fmt(v, 2) for v in rsi_.get("recent", []))
            return (
                header
                + f"RSI({rsi_.get('period', 14)}): {_fmt(value, 2)} — {_rsi_label(value)}\n"
                + f"Last 6 hourly values (oldest→newest): {recent}\n"
                + "(>70 overbought, <30 oversold)"
            )

        if name in ("stochastic", "stoch", "stochasticoscillator"):
            stoch = m.get("stochastic", {})
            k_val, d_val = stoch.get("k"), stoch.get("d")
            return (
                header
                + f"Stochastic(14,3,3): %K {_fmt(k_val, 2)} / %D {_fmt(d_val, 2)}\n"
                + f"State: {_stoch_label(k_val, d_val)}\n"
                + "(>80 overbought, <20 oversold)"
            )

        if name == "ema":
            ema_ = m.get("ema", {})
            custom = m.get("ema_custom")
            if period > 1 and custom:
                value = custom.get("value")
                rel = "above" if value is None or m["close"] >= value else "below"
                return header + f"EMA{custom['period']}: {_fmt(value)} (price is {rel} EMA{custom['period']})"
            return (
                header
                + f"EMA9:  {_fmt(ema_.get('9'))}\nEMA21: {_fmt(ema_.get('21'))}\nEMA50: {_fmt(ema_.get('50'))}\n"
                + f"Close: {_fmt(m['close'])}"
            )

        # macd
        macd_ = m.get("macd", {})
        hist = macd_.get("histogram") or 0
        state = "bullish (MACD > Signal)" if hist > 0 else "bearish (MACD < Signal)"
        return (
            header
            + f"MACD(12,26,9): {_fmt(macd_.get('line'))}\nSignal: {_fmt(macd_.get('signal'))}\n"
            + f"Histogram: {_fmt(macd_.get('histogram'))}\nState: {state}"
        )

    except ValueError as e:
        return f"❌ {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching indicator: Network error - {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"


@mcp.tool(
    annotations=ToolAnnotations(
        title="CryptoWeather Signal Guide",
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def get_signal_history() -> str:
    """크립토웨더(CryptoWeather) 시그널의 업데이트 주기와 해석 방법(방법론)에 대한 안내를 제공합니다."""
    return """🕐 CryptoWeather Signal Information
========================================
Supported Assets: Bitcoin (btc), Ethereum (eth), ADA (ada)
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
    # Debug output if enabled
    if args.debug:
        print("Starting CryptoWeather MCP Server...", file=sys.stderr)
        print(f"API Base: {CRYPTOWEATHER_BASE_URL}", file=sys.stderr)

    try:
        if os.getenv("PORT") or os.getenv("RENDER"):
            print(
                f"Starting CryptoWeather MCP Server (Streamable HTTP) on 0.0.0.0:{PORT}",
                file=sys.stderr,
            )
            mcp.run(transport="streamable-http")
        else:
            mcp.run()
    except Exception as e:
        print(f"Failed to start MCP server: {e}", file=sys.stderr)
        sys.exit(1)

# Main execution
if __name__ == "__main__":
    main()
