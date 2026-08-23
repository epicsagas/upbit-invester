---
name: upbit-portfolio
description: >-
  Upbit 계좌·포트폴리오 점검 스킬. "내 포트폴리오 봐줘", "보유 코인 점검", "수익률 어때",
  "리밸런싱 필요해?" 요청 시 계좌 조회 + 보유별 지표 진단 + 집중도 리스크를 평가한다.
  Account & portfolio review — holdings diagnosis plus concentration risk.
---

# upbit-portfolio — account & portfolio review

Keys required (`UPBIT_ACCESS_KEY`/`UPBIT_SECRET_KEY`). Read-only — no orders.

## Procedure

1. **Accounts**: `python3 scripts/upbit.py accounts`
   — currency, balance, avg_buy_price, valuation per coin.
2. **Per-holding diagnosis**: for each held market run
   `python3 scripts/upbit.py candles <market> --unit days --count 200 | python3 scripts/indicators.py`
   — price vs avg buy (return), trend, RSI (overbought/oversold), ATR
   (re-derive stop distance).
3. **Concentration analysis**:
   - single coin weight > max_single (preset default 15%) ⇒ warn
   - total invested weight > max_total (50%) ⇒ warn
   - day PnL / cash ≤ −3% (conservative limit) ⇒ kill-switch warning
4. **Past-decision comparison**: 
   `grep '"market": "KRW-XXX"' ~/.upbit-investor/decisions.jsonl | tail -3`
   — trajectory vs prior calls: on track, or stop condition reached.
5. **Recommendations**: hold / stop out / partial take-profit / rebalance —
   1-2 lines of rationale each.

## Output format

```markdown
# Portfolio Review (2026-08-23)
## Holdings — table: market/qty/avg buy/price/return/weight
## Per-coin diagnosis — trend·RSI·stop distance
## Risk — concentration/day PnL/gate status
## Recommendations — hold/act list + reasons
```

## Formulas

- return = (price − avg_buy_price) / avg_buy_price; valuation = balance × price
- total assets = cash (KRW) + Σ valuations; weight = valuation / total assets
- recommendations cite numbers; execution goes through upbit-trade only
  (user confirmation mandatory).
