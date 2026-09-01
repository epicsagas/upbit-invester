**[English](README_EN.md)** | [한국어](README.md)

<center><h1>upbit-investor</h1></center>

> Pit the buy case against the sell case head-on, then carry the verdict through risk checks and your own decision history into a final investment report.

An Upbit coin investment plugin that runs on Claude Code, Codex, Antigravity, and Hermes Agent. Market data, screening, technical indicators, backtesting, portfolio review, and order execution in one bundle — with the centerpiece being an 8-stage role-separated analysis pipeline (table below). Buy/sell orders never fire automatically; your explicit confirmation is always the last gate.

## Install

```bash
# Claude Code
claude plugin marketplace add epicsagas/upbit-invester
claude plugin install upbit-investor@upbit-investor

# Codex
codex plugin marketplace add epicsagas/upbit-invester
codex plugin add upbit-investor@upbit-investor

# Antigravity
agy plugin install https://github.com/epicsagas/upbit-invester

# Hermes Agent — the install scanner flags this plugin's AGENTS.md guide as a
# CRITICAL "persistence" finding (a heuristic that catches any agent-config
# file reference). Disable install scanning, install, then re-enable:
hermes config set plugins.scan_on_install false
hermes plugins install https://github.com/epicsagas/upbit-invester --enable
hermes config set plugins.scan_on_install true
hermes gateway restart
```

## Quick Start

Prerequisites: Python 3.10+ and an agent host. Quotes and analysis need no API
keys — account queries and orders do.

```
You: "Analyze KRW-BTC"            → full 8-stage pipeline
You: "Pick coins by volume"       → screening + per-candidate summary
You: "Backtest KRW-BTC"           → strategy returns vs buy-and-hold benchmark
You: "What's the BTC price now?"  → ticker/orderbook/candle facts
```

To connect an account, issue a key at Upbit → My Page → API Management and
export it. Read-only scope is recommended to start — everything analytical
works, and you can add order scope later. Never paste keys into chat or code;
environment variables only:

```bash
export UPBIT_ACCESS_KEY="..."
export UPBIT_SECRET_KEY="..."
```

## How It Works

One sentence — "Analyze KRW-BTC" — runs the 8 stages below in order, each
stage's output feeding the next. Not a vote: a hierarchy of judges, so evidence
accumulates downward.

| | Stage | What happens |
|--|-------|--------------|
| 📸 | Snapshot | daily/minute candles, ticker, orderbook, trades, indicator JSON, recent news, and recalled past decisions — gathered in one bundle |
| 👁 | Market analyst | trend, volatility, volume anomalies summarized in a few sentences |
| 🐂 | Bull researcher | argues the buy case with snapshot numbers (round 1) |
| 🐻 | Bear researcher | argues the sell/wait case independently (round 1) |
| ⚔️ | Debate round 2 | each side directly rebuts the other's round-1 arguments |
| 🧑‍⚖️ | Research manager | judges the debate by evidence quality — rating/confidence/target JSON |
| 🛡 | Risk manager | runs the 6 risk gates and sizes the position |
| 📊 | Portfolio manager | cross-checks past decisions, issues the final call (may override) |
| 📝 | Trader | order proposal with entry, stop-loss, split entries — **proposal only** |

When the report lands, the verdict is journaled as one line in
`~/.upbit-investor/decisions.jsonl` and recalled the next time you analyze the
same coin — the pipeline checks its own past calls for consistency and
direction flips.

Sibling skills: `upbit-market-data` (quote facts), `upbit-technical`
(indicator reading), `upbit-screen` (screening), `upbit-backtest` (strategy
validation + correlation), `upbit-portfolio` (holdings review), `upbit-trade`
(order execution past the confirm gate).

## Safety rails

| Rail | What it does |
|------|--------------|
| Confirmation gate | always asks the user before any order |
| 6 risk gates | single-coin weight, total exposure, overheat block, order rate, daily loss limit |
| Kill switch | daily loss limit breach blocks all further buy proposals (hard) |
| Round-down sizing | quantities always rounded down — never overspends cash |
| Fees applied | KRW markets 0.05% / BTC·USDT markets 0.25%, charged both legs in backtests |
| No withdrawals | the plugin never touches withdrawal APIs |

Risk presets: `conservative` (default) / `momentum` / `long_term`.

## FAQ

<details>
<summary>Can I try it without API keys?</summary>

Yes. Quotes, candles, orderbook, trades, screening, indicators, and backtests
all use the public API. Account queries and orders need a key; without one,
analysis stays read-only.

</details>

<details>
<summary>Does it auto-trade?</summary>

No. The pipeline only *proposes* orders; execution happens in the upbit-trade
skill's confirmation gate, only after you say yes. Withdrawals are not
supported at all.

</details>

<details>
<summary>How much data do backtests use?</summary>

The REST API gives the last 200 bars; `scripts/history.py` pulls full
daily/weekly/monthly history from the crix ZIP archives (locally cached).
Prefer 1-2 year windows — thin trade counts make the statistics meaningless.

</details>

<details>
<summary>Buys are blocked with "daily loss limit exceeded".</summary>

That's the kill switch (gate 6, hard). Under the conservative preset, a day
loss beyond −3% of cash blocks every further buy proposal. Change the preset
or wait for the next day.

</details>

<details>
<summary>Indicators look wrong.</summary>

Run `python3 scripts/test_indicators.py` — the indicator math self-check.
If it passes, the computation is sound; interpretation thresholds live in
the `upbit-technical` skill's reading table.

</details>

## Direct script usage (no agent)

```bash
python3 scripts/upbit.py ticker KRW-BTC
python3 scripts/upbit.py candles KRW-BTC --unit days --count 200 | python3 scripts/indicators.py
python3 scripts/history.py KRW-BTC --start 2024-08-01   # full history (crix ZIP, cached)
python3 scripts/screen.py --top 10 --sort gainers
python3 scripts/backtest.py sma_cross --file /tmp/btc.json
python3 scripts/test_indicators.py   # indicator math self-check
```

Python standard library only — nothing to install.

## Acknowledgements

This plugin builds on the design and material of four projects.

**[TradingAgents](https://github.com/tauricresearch/tradingagents)** (Tauric Research) — the backbone of the analysis pipeline. The multi-agent debate structure (bull and bear researchers over multiple rounds), the hierarchy of research/risk/portfolio/trader judges, and the idea of journaling past decisions and recalling them in later analyses all come from here.

**[upbit-agent-skills](https://github.com/upbit-official/upbit-agent-skills)** — design conventions from Upbit's official agent skill: bilingual trigger descriptions in skill frontmatter, per-endpoint reference layout, and the user-confirmation gate before write operations.

**[upbit-cli](https://github.com/upbit-official/upbit-cli)** — the API command surface (ticker/candles/orderbook/orders/DCA/polling TP-SL), the API key precedence pattern (flags > env > config file), and the `X-Upbit-Initiator` header convention.

**[upbit-strategy-toolkit](https://github.com/upbit-official/upbit-strategy-toolkit)** — backtesting conventions: the crix ZIP archive data path for full candle history, per-market fee/min-order/tick rules, and engine rules such as next-bar-open entry and stop-loss-first liquidation priority.

## License

MIT. Copyright © 2026 epicsagas.

## Disclaimer

This plugin ("upbit-investor") is a software tool. It is NOT a financial or
investment advisory service and does not conduct any activity that would
constitute investment advice or asset management under the securities,
capital-markets, or financial-services regulations of any jurisdiction.

1. **Nature of information.** All analyses, indicator interpretations, ratings
   (Buy/Hold/Sell or similar), price targets, and order proposals produced by
   this plugin are reference information derived from public data and
   statistical models. They do not constitute a recommendation, solicitation,
   or offer to buy or sell any cryptocurrency, nor any promise of profit or
   protection against loss.
2. **Investment responsibility.** Cryptocurrencies are high-risk assets that
   can lose principal. Past performance and backtest results do not guarantee
   future returns. Full responsibility for every investment decision and its
   outcome rests solely with the user.
3. **Data accuracy.** Market and indicator data come from the Upbit public API
   and may contain transmission delays, outages, or errors. Before executing
   any order, the user must verify final prices and conditions against the
   exchange's official information.
4. **Software defects.** This software is provided "AS IS", without warranty of
   any kind, express or implied, including but not limited to the warranties of
   merchantability, fitness for a particular purpose, and non-infringement. The
   developers shall in no event be liable for any direct, indirect, incidental,
   or consequential damages arising from software defects, malfunction, or data
   errors.
5. **API key management.** Issuing, storing, and scoping Upbit API keys is the
   user's responsibility; all losses caused by key leakage are borne by the
   user. Use order-scoped keys only when necessary and with minimal
   permissions.
6. **Tax and legal compliance.** Complying with tax obligations and applicable
   laws related to cryptocurrency trading is the user's duty. This plugin does
   not provide tax or legal advice.

Installing or using this plugin constitutes acceptance of all of the above
terms.
