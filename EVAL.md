# Eval Report — upbit-investor v0.1.0

- Date: 2026-08-24 (KST)
- Scope: plugin at `/Volumes/T5/projects/epicsagas/upbit-plugin/upbit-investor`
- Harness: epic eval (`epic eval --json`), domain benchmark `benchmarks/eval_runner.py`
- Constraint honored: **no real orders were placed at any point** — public and
 read-only endpoints only (markets/ticker/candles/orderbook/trades). The
 order/withdraw code paths were exercised only by code review and unit
 self-checks, never against the live API.

## Overall: PASS — 1.00

| Dimension | Verdict | Score | Evidence |
|-----------|---------|-------|----------|
| Benchmark (domain) | PASS | 1.0 | composite from 4 subscores below |
| Correctness | PASS | 1.0 | indicator math self-checks + live schema validation |
| Performance | PASS | n/a | avg 98 ms per live endpoint (informal, within budget) |
| Quality (LLM-as-judge) | PASS | 0.82 | 4-axis rubric on 4 core files |
| Regression | PASS | — | first run — baseline established and saved |
| Structure (forge doctor) | PASS | — | 24 PASS / 3 WARN / 0 FAIL |
| Claude CLI validation | PASS | — | `claude plugin validate` passed |

## Subscores

| Check | Weight | Result | Detail |
|-------|--------|--------|--------|
| indicator_math | 0.4 | 1.0 | `scripts/test_indicators.py` — exponential/quadratic trend reads, RSI bounds 0-100, MACD flip, short-series nulls |
| live_api | 0.3 | 1.0 | ticker, daily/minute candles, orderbook, trades all 200 OK |
| indicator_schema | 0.2 | 1.0 | all 8 required fields present, RSI within [0,100] |
| structure | 0.1 | 1.0 | 7 skills / 7 agents / 5 scripts present |

Live latency per endpoint: ticker 111 ms · daily candles 118 ms · minute
candles 84 ms · orderbook 86 ms · trades 91 ms (first benchmark run; repeated
runs similar).

## LLM-as-judge detail (rubric 1-10, 4 files)

| File | Readability | Correctness | DRY | Security |
|------|-------------|-------------|-----|----------|
| scripts/indicators.py | 8 | 8 | 7 | 9 |
| scripts/upbit.py | 8 | 8 | 8 | 8 |
| skills/upbit-investor/SKILL.md | 9 | 8 | 9 | 9 |
| agents/research-manager.md | 9 | 8 | 9 | 9 |

Average 8.2/10 → 0.82. Findings already fixed during eval: stochastic
tie-penalty bug, trend-score reachability bug, test path-resolution bug.

## Bugs found and fixed during eval

1. **stochastic equality penalty** — k == d was scored as a bearish vote;
 now skipped (only strict k<d penalizes).
2. **unreachable trend threshold** — fixed threshold (±3 of ±5) was
 unattainable when some signals were null; replaced with a 60% majority of
 *available* directional signals. RSI removed from the direction score
 (overbought is an overlay, not a direction).
3. **test path resolution** — `test_indicators.py` invoked `indicators.py`
 via a cwd-relative path; now resolved relative to its own file.

## Validation matrix (host manifests)

| Host | Check | Result |
|------|-------|--------|
| Claude Code | `.claude-plugin/plugin.json` + marketplace + `claude plugin validate` | PASS |
| Codex | `.codex-plugin/plugin.json` + 7 TOML agents, md↔toml coverage | PASS |
| agy | root `plugin.json` discoverable | PASS |
| hermes | root `plugin.yaml` + `__init__.py` register() + 7 provides_skills | PASS (scan-on-install may warn on AGENTS.md — documented workaround in README) |

## Known limitations

- Backtest excludes fees and slippage (documented in-skill).
- Decision memory is a JSONL journal, not a full FTS5+vector hybrid —
 recall precision degrades past a few hundred decisions (upgrade path noted
 in references/memory.md).
- No realized-P&L reflection stage.
- Deep/quick LLM tiers are not distinguished — the pipeline relies on host
 model selection.

## v2 pass (post ref-toolset full report)

The full ref toolset inventory (upbit-agent-skills / upbit-cli /
upbit-strategy-toolkit) arrived after the initial ship. Gaps closed:

1. **Full history beyond the REST 200-bar cap** — new `scripts/history.py`
 fetches daily/weekly/monthly ZIP partitions from crix-data.upbit.com
 (pattern from upbit-strategy-toolkit), parallel (8 threads, ~0.2 s per 2
 months cold, ~0 ms cached), emitted in REST candle shape so
 indicators/backtest consume it unchanged. Verified: 731 daily bars
 (2024-08 → 2026-08) feeding indicators + backtest end-to-end.
2. **X-Upbit-Initiator header** on every API call (official convention).
3. **Backtest fees** — applied on both legs, `--fee` flag; default 0.05%
 (KRW), 0.25% for BTC/USDT-quoted markets (per market_rules.json).
4. **New indicators** — ADX14 (Wilder, ±DI), Williams %R, CCI20, disparity
 vs SMA — with self-check assertions (bounds, direction, null-on-short).
5. **Fee docs corrected** across risk-gates / trade skill / trader agent.

Re-run after v2: self-checks pass, forge doctor 24 PASS / 0 FAIL, epic eval
overall **1.0 PASS**.

## Conclusion

All dimensions PASS, first baseline saved
(`/Users/hackme/.harness/projects/upbit-investor/eval/baselines/latest.json`).
Ready to commit/push. Future runs compare against this baseline
(threshold 0.05).
