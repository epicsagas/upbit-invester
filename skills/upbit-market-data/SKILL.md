---
name: upbit-market-data
description: >-
  Upbit 시장 데이터 수집 스킬. "지금 BTC 시세", "이더리움 호가", "캔들 데이터 보여줘",
  "거래대금 높은 코인", "KRW 마켓 목록" 요청 시 candles/ticker/orderbook/trades/markets를
  수집해 정리한다. 분석 없이 데이터 팩트만 제공. Upbit market data collection —
  price/orderbook/candles/trades facts without analysis.
---

# upbit-market-data — market data collection

Public API only — no keys. All commands run from the plugin root `scripts/`.

## Commands

| Purpose | Command |
|---------|---------|
| All KRW markets | `python3 scripts/upbit.py markets --quote KRW` |
| Multiple tickers | `python3 scripts/upbit.py ticker KRW-BTC KRW-ETH` — trade_price, change_rate, acc_trade_price_24h |
| Daily 200 | `python3 scripts/upbit.py candles KRW-BTC --unit days --count 200` (oldest-first) |
| 60-min candles | `python3 scripts/upbit.py candles KRW-BTC --unit minutes --minute 60 --count 200` (minute: 1,3,5,10,15,30,60,240) |
| Weekly/monthly | `--unit weeks` / `--unit months` |
| Order book | `python3 scripts/upbit.py orderbook KRW-BTC` — 15-level book, total_ask/bid_size |
| Recent trades | `python3 scripts/upbit.py trades KRW-BTC --count 50` — up_down (aggressor) |
| Min order/tick | `python3 scripts/upbit.py chance KRW-BTC` (keys required) |

## Interpretation guide

- **Supply balance**: `total_bid_size` > `total_ask_size` means bid-side
  dominance — not a standalone signal (spoof orders possible). Cross-check
  with trade `up_down`.
- **Volume anomaly**: compare ticker `acc_trade_price_24h` against the recent
  daily average — per-day trend via candle `candle_acc_trade_volume`.
- **Flash move**: |change_rate| > 5% ⇒ flag "flash move" in the snapshot.

## Output format

A table (market / price / day change / 24h volume). For candle requests,
report key stats (last 5 bars OHLCV) instead of the full JSON; save the raw
JSON to a file and give the path.
