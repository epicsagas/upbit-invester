---
name: upbit-trade
description: >-
  Upbit 주문 실행 스킬. "매수해줘", "KRW-BTC 팔아줘", "지정가 주문", "분할매수",
  "손절 주문 넣어줘" 요청 시 — 사용자 명시 확인 후에만 실제 주문을 실행한다.
  확인 전에는 절대 주문 API를 호출하지 않는다. Order execution — only after explicit
  user confirmation; never calls order APIs before the confirm gate.
---

# upbit-trade — order execution (confirmation gate mandatory)

## Absolute rules

1. **Never call an order API until the user explicitly answers "confirm"/"yes"/
   "go".** Requests that are analysis-only ("should I buy?") redirect to the
   upbit-investor skill.
2. Keys required: `UPBIT_ACCESS_KEY` / `UPBIT_SECRET_KEY` — abort with guidance
   if absent.
3. Check the 6 risk gates (risk-gates.md) before ordering — refuse all buys
   when the kill switch is armed.
4. Withdrawals are NOT supported by this skill. Security: users withdraw via
   the Upbit app themselves.

## Pre-order checks

```bash
python3 scripts/upbit.py chance KRW-BTC   # min order 5,000 KRW, tick, volume unit
python3 scripts/upbit.py accounts         # cash + holdings
python3 scripts/upbit.py ticker KRW-BTC   # current price (price_band gate)
```

Adjust price/quantity to tick units (round DOWN), keep a fee margin (KRW
markets 0.05%, BTC/USDT markets 0.25%).

## Order commands

| Purpose | Command |
|---------|---------|
| Market buy (KRW amount) | `python3 scripts/upbit.py order buy KRW-BTC --price 10000` |
| Limit buy | `python3 scripts/upbit.py order buy KRW-BTC --price 50000000 --volume 0.001` |
| Market sell (quantity) | `python3 scripts/upbit.py order sell KRW-BTC --price 0 --volume 0.05`* |
| Open orders | `python3 scripts/upbit.py orders --state wait` |
| Cancel | `python3 scripts/upbit.py cancel <uuid>` |

*Market sells require `--volume` — for a full exit, read the holding from
accounts first. (`--price` is syntactically required but ignored for market
sells.)

## Confirmation format

Always confirm with the user in this shape before ordering:

```
주문 확인 요청
- 마켓: KRW-BTC
- 구분: 시장가 매수
- 금액: 10,000 KRW (예상 수량 0.000094 BTC)
- 손절 계획: 101,500,000 (진입 − 1.5×ATR)
- 수수료: 약 5 KRW
실행할까요? (예/아니오)
```

## After ordering

1. Report the `uuid` immediately.
2. Offer cancellation for unfilled limit orders.
3. Append the fill to `~/.upbit-investor/decisions.jsonl` as one line
   (`"executed": true, "filled_price": ...`).

## Supported strategies (on request)

- **DCA**: split a buy into n market orders at the stated interval — respect
  the per-minute order gate.
- **Stop-loss limit**: after a fill, place a limit sell at entry − 1.5×ATR.
- **TP/SL set**: place both target and stop limit orders — Upbit has no OCO,
  so tell the user the other side must be cancelled manually after one fills.
