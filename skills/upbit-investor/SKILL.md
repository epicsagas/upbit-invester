---
name: upbit-investor
description: >-
 Upbit 코인 투자 종합 분석·의사결정 오케스트레이터. "KRW-BTC 분석해줘", "이 코인 사도 될까",
 "포트폴리오 점검", "매매 신호 봐줘", "코인 투자 판단" 요청 시 8단계 멀티 역할 분석 파이프라인
 (스냅샷 → 시장분석 → 불/곰 디비트 2라운드 → 리서치 매니저 판정 → 리스크 게이트 →
 포트폴리오 판단 → 트레이더 제안)으로 최종 투자 보고서를 낸다. Full Upbit coin investment
 decision orchestrator — 8-stage multi-role pipeline producing a final report.
---

# upbit-investor — 8-stage pipeline orchestrator

Runs an 8-stage hierarchical debate pipeline on Upbit KRW markets. Hierarchical
judge structure — no voting; each stage's verdict is inherited by the next.

## Absolute rules

1. **Never place a real order without explicit user confirmation.** Analysis
 and proposal stages never call order APIs. Execution is delegated to the
 upbit-trade skill.
2. Public endpoints (markets/ticker/candles/orderbook/trades) need no keys.
 Accounts/orders need `UPBIT_ACCESS_KEY`/`UPBIT_SECRET_KEY` — if absent,
 read-only analysis only.
3. All scripts are stdlib-only Python under the plugin root `scripts/`.

## Tooling

| Step | Command |
|------|---------|
| Market list | `python3 scripts/upbit.py markets --quote KRW` |
| Ticker | `python3 scripts/upbit.py ticker KRW-BTC KRW-ETH` |
| Candles | `python3 scripts/upbit.py candles KRW-BTC --unit days --count 200` |
| Full history | `python3 scripts/history.py KRW-BTC --start 2024-08-01` (crix ZIP archives, cached) |
| Indicators | `python3 scripts/upbit.py candles KRW-BTC --unit days --count 200 \| python3 scripts/indicators.py` |
| Orderbook | `python3 scripts/upbit.py orderbook KRW-BTC` |
| Trades | `python3 scripts/upbit.py trades KRW-BTC --count 50` |
| Accounts (keys) | `python3 scripts/upbit.py accounts` |
| Screening | `upbit-screen` skill |

## 8-stage pipeline

Full per-stage prompts live in `references/pipeline.md`. Summary:

1. **Snapshot** — daily 200 + 60-min 200 candles, ticker, orderbook, indicator
 JSON. Snapshot extension: orderbook/trades/indicators included
 (classic debate designs often omit them). News/macro via web tools when available (optional).
2. **Market analyst (quick)** — 5-line summary: trend/volatility/volume
 anomaly/indicator read.
3. **Bull vs Bear round 1** — 3-5 independent arguments each. No unsupported
 claims; every number cites the snapshot.
4. **Round 2 (rebuttal)** — directly attack the opponent's round-1 arguments.
5. **Research manager verdict** — 5-tier JSON judging the debate:
 `{"direction": "bullish|bearish|neutral", "confidence": 0-100, "debate_winner": "bull|bear|tie",
 "key_arguments": [...], "price_target": float|null, "time_horizon": "short|mid|long"}`
6. **Risk manager overlay** — 6-gate pass/fail + position sizing
 (cash × risk pct ÷ entry, rounded down). See `references/risk-gates.md`.
7. **Portfolio manager decision** — past-decision recall injected (grep the
 market's prior entries in `~/.upbit-investor/decisions.jsonl`), then final
 override: enter / wait / exit.
8. **Trader proposal** — `propose_order` JSON: market/limit, target, stop-loss
 (entry − 1.5×ATR), split entries. **Proposal only — execution requires user
 confirmation via the upbit-trade skill.**

## Output format (final report)

```markdown
# KRW-BTC Investment Analysis (2026-08-23)
## Snapshot — price/trend/volume key numbers
## Market analysis — 5-line summary
## Bull vs Bear — round-1 arguments + round-2 rebuttal gist
## Research manager verdict — direction/confidence/price_target
## Risk — gate results + proposed position size
## Portfolio decision — final call with past-decision recall
## Trader proposal — propose_order JSON + stop/target rationale
## Conclusion — one paragraph: buy / wait / sell + top 3 reasons
```

After the verdict, append one line to `~/.upbit-investor/decisions.jsonl`
(schema in `references/memory.md`).

## Intents -> actions

| User intent | Action |
|-------------|--------|
| "KRW-XXX 분석해줘" | full 8-stage run |
| "이 코인 사도 될까?" | 8 stages + concrete entry plan |
| "지금 포트폴리오 점검해줘" | hand off to `upbit-portfolio` |
| "백테스트해줘" | hand off to `upbit-backtest` |
| "매수/매도해줘" | analyze, then after confirmation → `upbit-trade` |
| "뭐 좀 골라봐" | `upbit-screen` screening → short summary per candidate |
