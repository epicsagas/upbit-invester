# upbit-investor

[한국어](./README.md)

Multi-agent analysis & trading plugin for Upbit (Korean crypto exchange). Runs on four hosts — Claude Code, Codex, agy, hermes. Ports deep-analysis pipeline (bull/bear debate → verdict → risk gates → order proposal) to Upbit KRW markets, and bundles market data, screening, backtesting, and portfolio review into one plugin.

**No order is ever placed automatically.** Every order requires explicit user confirmation.

---

## Quick Start (Beginners)

### Step 1 — no keys needed (market data only)

Works immediately after install:

```
"비트코인 지금 시세 어때?" ("What's the BTC price?")
"KRW-BTC 호가창 보여줘" ("Show the KRW-BTC order book")
"거래대금 많은 코인 Top 10" ("Top 10 by volume")
"KRW-BTC 기술적 지표 분석해줘" ("Analyze KRW-BTC indicators")
```

### Step 2 — full investment analysis

```
"KRW-BTC 분석해줘" runs the full 8-stage pipeline
"이 코인 사도 될까?" analysis + entry strategy proposal
```

### Step 3 — connect your account (API keys)

1. Issue a personal API key at Upbit → My Page → API Management. Security tip: read-only scope is enough for all analysis.
2. Export the keys:

```bash
export UPBIT_ACCESS_KEY="..."
export UPBIT_SECRET_KEY="..."
```

3. Now available:

```
"내 포트폴리오 점검해줘" ("Review my portfolio")
"KRW-BTC 10만원어치 매수해줘" ("Buy 100k KRW of KRW-BTC") — runs only after a confirmation prompt
```

> 💡 Start with a read-only key; add order scope later when you trust the workflow. Never paste keys into chat — environment variables only.

---

## What it does (the whole map)

```
┌─ Discover ───────────────────────────────────────────────┐
│ upbit-screen "pick something" — volume/gainer/loser │
└──────────┬───────────────────────────────────────────────┘
 ▼
┌─ Analyze ─ upbit-investor (main, 8-stage 8-stage pipeline) ─┐
│ 1 snapshot candles·ticker·orderbook·indicators·news │
│ 2 market analyst 3-4 sentence trend/vol/volume summary │
│ 3 bull vs bear debate — round 1 independent arguments │
│ 4 bull vs bear debate — round 2 direct rebuttals │
│ 5 research manager verdict JSON (rating/confidence) │
│ 6 risk manager 6-gate check + position sizing │
│ 7 portfolio manager past-decision recall + final call │
│ 8 trader order proposal JSON (entry/stop) │
│ │
│ underlying skills: upbit-market-data / upbit-technical │
└──────────┬───────────────────────────────────────────────┘
 ▼
┌─ Validate ────────────────────────────────────────────────┐
│ upbit-backtest SMA-cross / RSI-reversion · correlation │
└──────────┬────────────────────────────────────────────────┘
 ▼
┌─ Execute & Manage ───────────────────────────────────────┐
│ upbit-trade real orders only past the confirm gate │
│ upbit-portfolio holdings review · concentration risk │
└──────────────────────────────────────────────────────────┘
```

Every conclusion is journaled to `~/.upbit-investor/decisions.jsonl` and
recalled in later analyses, so the pipeline remembers its own past calls.

## Safety rails

| Rail | What it does |
|------|--------------|
| Confirmation gate | always asks the user before any order |
| 6 risk gates | single-coin weight, total exposure, overheat block, daily loss limit, … |
| Fees applied | KRW markets 0.05% / BTC·USDT markets 0.25% (charged both legs in backtests) |
| Kill switch | daily loss limit breach blocks all further buy proposals (hard) |
| Round-down sizing | quantities always rounded down — never overspends cash |
| No withdrawals | the plugin never touches withdrawal APIs |

Risk presets: `conservative` (default) / `momentum` / `long_term`.

## Install

### Claude Code

```bash
claude plugin install epicsagas/upbit-investor
# or locally: claude plugin install /path/to/upbit-investor
```

### Codex

```bash
codex plugin add epicsagas/upbit-investor
```

### agy

Copy the folder to `~/.agy/plugins/upbit-investor/` and restart.

### hermes

Copy the folder to `~/.hermes/plugins/upbit-investor/` and restart.
> If the install scanner warns about `AGENTS.md` (CRITICAL persistence), pass it with `hermes plugins install --force` (or disable `plugins.scan_on_install`).

## Layout

```
skills/ 7 skills (SKILL.md is the source of truth for every host)
 upbit-investor/ main 8-stage pipeline + references/ (debate·risk·memory)
 upbit-market-data/ upbit-technical/ upbit-screen/
 upbit-backtest/ upbit-portfolio/ upbit-trade/
agents/ 7 sub-agents (analyst·bull·bear·research·risk·portfolio·trader)
scripts/ stdlib-only Python — upbit.py(API) indicators.py history.py screen.py backtest.py
```

## Direct script usage (no agent)

```bash
python3 scripts/upbit.py ticker KRW-BTC
python3 scripts/upbit.py candles KRW-BTC --unit days --count 200 | python3 scripts/indicators.py
python3 scripts/history.py KRW-BTC --start 2024-08-01 # full history (crix ZIP, cached)
python3 scripts/screen.py --top 10 --sort gainers
python3 scripts/backtest.py sma_cross --file /tmp/btc.json
python3 scripts/test_indicators.py # indicator math self-check
```

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
