# AGENTS.md — upbit-investor

> Shared agent guide. Claude Code, Codex, agy, and hermes all load this file.

## Role

Upbit coin investment plugin: market data → 8-stage pipeline multi-role analysis → risk-gated
order PROPOSALS. Ports 8-stage deep-analysis FSM (snapshot →
market analyst → bull/bear debate ×2 rounds → research manager → risk manager →
portfolio manager → trader) to Upbit KRW markets. The authoritative workflow is
`skills/upbit-investor/SKILL.md` (+ its `references/`); sibling skills cover
data, indicators, screening, backtest, portfolio, execution.

## Absolute rules

1. NEVER call order/withdraw endpoints without explicit user confirmation.
 Analysis and proposals only. Execution goes through the upbit-trade skill's
 confirmation gate. Withdrawals are never supported.
2. Public endpoints (markets/ticker/candles/orderbook/trades) need no keys.
 Accounts/orders need `UPBIT_ACCESS_KEY` / `UPBIT_SECRET_KEY` — when absent,
 read-only analysis only.
3. Scripts are stdlib-only Python in `scripts/` — run with `python3 scripts/...`
 from the plugin root.

## Pipeline skills (dispatch by intent)

| Intent | Skill |
|--------|-------|
| "KRW-XXX 분석해줘" / full investment decision | upbit-investor |
| "지금 시세", "호가", "캔들" | upbit-market-data |
| "RSI/MACD/추세 확인" | upbit-technical |
| "급등/거래대금 상위 골라줘" | upbit-screen |
| "백테스트", "상관관계" | upbit-backtest |
| "포트폴리오 점검" | upbit-portfolio |
| "매수/매도해줘" (after confirm) | upbit-trade |

Sub-agents (Claude Code dispatch): market-analyst, bull-researcher,
bear-researcher, research-manager, risk-manager, portfolio-manager, trader —
one per pipeline stage; prompts in `agents/*.md`.

## Host differences

- **Claude Code**: skills + `agents/` sub-agents.
- **Codex**: same skills; agents converted to `.codex-plugin/agents/*.toml`.
- **agy / hermes**: skills only — run the pipeline roles inline, sequentially.
