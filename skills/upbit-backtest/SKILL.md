---
name: upbit-backtest
description: >-
 Upbit 전략 백테스트 스킬. "백테스트해줘", "SMA 크로스 전략 성과 어때", "RSI 반전 전략",
 "BTC ETH 상관관계" 요청 시 캔들 데이터로 전략 성과 지표와 상관계수를 계산한다.
 Strategy backtest (SMA cross / RSI reversion) and pairwise correlation.
---

# upbit-backtest — strategy backtest & correlation

initial cash 10,000,000 KRW, round-trip fees applied
on both legs (default 0.05%, `--fee` to override — BTC/USDT-quoted markets are
0.25%).

## Two strategies

| Strategy | Rule | Fits |
|----------|------|------|
| `sma_cross` | buy SMA5/20 golden cross, sell dead cross | trending |
| `rsi_reversion` | enter on RSI14 < 30 (buy next bar), exit on RSI14 > 70 | ranging |

## Commands

```bash
# last 200 bars via REST (quick)
python3 scripts/upbit.py candles KRW-BTC --unit days --count 200 > /tmp/btc.json
# full history via crix ZIP archives (day/week/month, cached) — use for >= 1y
python3 scripts/history.py KRW-BTC --start 2024-08-01 > /tmp/btc.json
python3 scripts/backtest.py sma_cross --file /tmp/btc.json
python3 scripts/backtest.py rsi_reversion --file /tmp/btc.json --fee 0.0025
python3 scripts/backtest.py correlate /tmp/btc.json /tmp/eth.json # pearson + beta
```

`history.py` fetches one ZIP per day/week/month from crix-data.upbit.com
(cold fetch ≈ 0.2 s per 2 months with 8 parallel downloads, then cached under
`~/.upbit-investor/cache/`). 403/404 partitions are normal at range edges —
not-yet-published data.

Metrics: total_return, cagr (252), win_rate, max_drawdown, sharpe, num_trades,
**buy_hold_return (benchmark)**.

## Interpretation rules

- Strategy return < buy_hold ⇒ "worse than simply holding" — state it.
- Prefer full-history runs (`history.py`, 1-2y) — 200-bar REST windows give
 few trades and weak statistics.
- num_trades ≤ 3 ⇒ sample too small — "statistically weak" warning.
- MDD beyond −20% conflicts with the conservative preset — risk warning.
- Backtests describe the past, not the future. Look-ahead guard: every fill
 happens at the bar AFTER the signal bar (already implemented in the script).
- Prefer ≥ 200 days of data — `--count 200`.

## Portfolio correlation

Pairs with pearson > 0.8 give no diversification — "effectively the same
asset exposure" warning. Beta is relative volatility (denominator = the
second asset's variance) — state which side is the denominator.
