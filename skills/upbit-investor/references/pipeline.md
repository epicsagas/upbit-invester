# 8-stage pipeline detail

Source: an 8-stage hierarchical debate pipeline.
Hierarchical judges — no voting. Each stage's output is inherited as input by
the next.

## Common anchor (prepend to every role prompt)

```
Analysis target: {korean coin name} (market code {KRW-XXX}, Upbit KRW market).
Analyze ONLY this coin. Every number must come from the real-time data below
(candles/ticker/orderbook/indicators JSON) as the single source of truth.
Never fabricate numbers absent from the data.
```

Core anti-hallucination device. Attach the snapshot data to the prompt.

## Snapshot composition (stage 1, gather_snapshot)

Upbit-extended — orderbook/trades/indicators/news included in the snapshot:

- ticker: price, day change, 24h volume
- daily 200 + 60-min 200 candles (`upbit.py candles`)
- indicator batch JSON (`indicators.py`): SMA20/60, EMA12/26, RSI14,
 MACD(12,26,9), Bollinger(20,2), ATR14, Stochastic, VWAP, OBV,
 returns (1/7/30d), trend
- orderbook: best bid/ask, total bid/ask size (supply balance)
- trades: last 50 ticks (aggressor direction)
- (keys) accounts: held quantity, unrealized P&L, cash
- (keys) KB recall 3: last 3 decisions for this market from
 `~/.upbit-investor/decisions.jsonl` —
 "- [YYYY-MM-DD] {rating} — confidence {n}% — thesis gist"
- (web tools) recent news headlines 3-5 — coins are news-sensitive

## Free-text stages (quick tier, concise Korean output)

Common tone: "You are a crypto investment analyst. Answer in concise,
evidence-based Korean." (Role prompts produce Korean output for the user while
instructions stay English.)

| Role | Prompt gist |
|------|-------------|
| Market analyst | "Technical/market analysis in 3-4 sentences: trend, volatility, volume anomaly, indicator read." |
| Bull round 1 | "You are the bull. Argue the BUY case in 2-3 strong sentences grounded in the market analysis." |
| Bear round 1 | "You are the bear. Argue the SELL/WAIT case independently in 2-3 sentences." |
| Bull round 2 | "Rebut the bear's round-1 claims." |
| Bear round 2 | "Rebut the bull's round-1 claims." |

Rules: every claim cites a snapshot number. No unsupported narratives.
A failed stage degrades to an empty placeholder — never abort the run
(resilient).

## Structured stages (deep tier, JSON enforced)

### Research manager (debate judge)

```json
{"rating": "Buy|Overweight|Hold|Underweight|Sell",
 "confidence": 0.0,
 "debate_winner": "bull|bear|tie",
 "key_thesis": "one sentence",
 "catalysts": ["catalyst 1", "..."],
 "risks": ["risk 1", "..."],
 "price_target": null,
 "time_horizon": "short|mid|long"}
```

Embed the example JSON verbatim in the prompt: "Different field names, arrays
where strings belong, explanations, or <think> blocks are forbidden."

### Risk manager (overlay)

```json
{"overall_risk": "Low|Medium|High",
 "risk_factors": ["..."],
 "mitigation": ["..."],
 "max_position_pct": 0}
```

Reflects the 6-gate outcome (risk-gates.md) into max_position_pct.

### Portfolio manager (final override)

```json
{"rating": "Buy|Overweight|Hold|Underweight|Sell",
 "executive_summary": "one paragraph",
 "investment_thesis": "single sentence, not an array",
 "price_target": 0,
 "time_horizon": "short|mid|long"}
```

Past-decision recall injected. If risk max_position_pct exceeds the preset
single-position cap, append "⚠ recommended max position exceeded — reduce
size" to the summary.

### Trader (order proposal)

```json
{"action": "Buy|Hold|Sell",
 "entry_price": 0,
 "position_size_pct": 0,
 "stop_loss": 0,
 "order_type": "market|limit",
 "rationale": "one sentence"}
```

"Hold: omit the remaining fields." Stop-loss default: entry − 1.5×ATR14.

## JSON parsing defenses (GLM/local-model hardening — full original kit)

1. Attempt 1: JSON schema enforced, temp 0.3. On failure:
2. Attempt 2: plain JSON mode, temp 0.1, suffix "[Output rules] Output exactly
 one JSON object. No code fences, no explanations, no long prose.",
 max_tokens doubled.
3. Pre-parse: strip `<think>` blocks, remove code fences, unwrap single-key
 objects (`{"result": {...}}` → inner), absorb field aliases, coerce "25%"
 → 25.0, join arrays where a string is expected.
4. Final failure → safe defaults (Hold / confidence 0 / risk Medium) with an
 explicit "parse failure, defaults used" note. Never abort the run.

## rating normalization (normalize_rating)

Absorb Korean/abbreviations: "매수"→Buy, "강력매수"→Buy, "OW"→Overweight,
"매도"→Sell, "보류"/"관망"→Hold. Unknown → Hold.

## Stage failure handling (resilient)

RM/risk/PM/trader failure: record the reason
(rate_limited|http_error|timeout|parse_failed) + a Warning + degrade to safe
defaults (Hold/Medium) and continue. The market analyst is pipeline-critical —
on failure, re-collect the snapshot once and retry; abort only if that fails.

## Decision journal append schema (after stage 8)

```json
{"market": "KRW-BTC", "date": "2026-08-23",
 "rating": "Buy", "confidence": 0.72, "price_target": 120000000,
 "time_horizon": "mid", "risk_grade": "Medium", "max_position_pct": 15,
 "order_proposed": false, "price_at_decision": 105981000,
 "key_thesis": "...", "supersedes": "<date of previous decision for this market>"}
```

`supersedes` links only to the immediately previous decision FOR THE SAME
market (temporal spine — linking against the whole recall set causes
cross-coin mislinks; this exact failure mode was measured at 14/25 bad links).
Track direction changes: code ratings as ±1/0, compare with the previous
decision — agrees_with / maintains / reverses / initiates.
