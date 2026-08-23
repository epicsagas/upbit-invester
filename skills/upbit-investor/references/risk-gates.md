# Risk — 6 gates

Every order proposal must pass 6 gates. Soft gates attach warnings; hard gates
block the proposal outright.

| # | Gate | Type | Rule |
|---|------|------|------|
| 1 | price_band | soft | order price beyond preset ±% of current price → warn (flash-move protection) |
| 2 | max_single_position | soft | (held + new) / total assets (cash + valuation) ≤ preset % |
| 3 | max_total_invested | soft | total invested share ≤ preset % |
| 4 | overheat/warning block | soft | day change > +30%, Upbit investment-warning market, or halted trading → entry blocked with warning |
| 5 | max_orders_per_minute | soft | rate-limit proposals (anti rapid-retry) |
| 6 | daily_loss_limit | **hard** | day PnL / cash ≤ −limit ⇒ kill switch — all further proposals blocked |

## Presets

| Preset | max_single | max_total | price_band | daily_loss | overheat block |
|--------|-----------|-----------|------------|-----------|----------------|
| conservative (default) | 15% | 50% | ±5% | −3% | on |
| momentum | 25% | 80% | ±10% | −8% | off |
| long_term | 20% | 60% | ±5% | −5% | on |

State the preset name in the report whenever the user overrides the default.

## Position sizing (calc_buy_quantity port)

```
quantity = floor(cash × max_position_pct/100 ÷ entry_price)
```

Always round DOWN (never round up — prevents overspending cash). Sells: full
holding or a specified quantity. Fees: KRW-quoted markets 0.05%, BTC/USDT-
quoted markets 0.25% (general tier) — keep a
cash margin for fees.

## Upbit minimums (mandatory pre-order check)

- Minimum order: 5,000 KRW on KRW markets (varies — confirm via
 `upbit.py chance`)
- Price tick: varies by price band — `chance` response `ask.price_unit`
- Volume unit: varies by market — `chance` response `market.ask.bid_unit`
 (typically 0.0001...)

Before ordering, run `python3 scripts/upbit.py chance KRW-XXX`, then adjust
price/quantity to tick units (round down).

## Kill switch (gate 6, hard)

On daily loss limit breach:
1. Block every further buy proposal (state the reason).
2. Propose full liquidation only with user confirmation.
3. Record the kill-switch event in `~/.upbit-investor/decisions.jsonl`.

Daily loss = (day-start assets − current total assets) / day-start cash.
When uncomputable, approximate with the sum of unrealized P&L and mark it as
approximate.
