---
name: upbit-screen
description: >-
  Upbit KRW 마켓 스크리닝 스킬. "거래대금 많은 코인", "오늘 급등 코인", "급락 코인",
  "투자 후보 골라줘", "52주 신고가 코인" 요청 시 조건 필터 후 후보 리스트를 뽑고
  필요시 상위 후보 지표 분석까지 이어간다. KRW market screening by volume/gainers/
  losers with follow-up indicator analysis.
---

# upbit-screen — market screening

## Commands

```bash
python3 scripts/screen.py --top 10 --min-volume 1e9 --sort volume   # top volume
python3 scripts/screen.py --top 10 --sort gainers                   # top gainers
python3 scripts/screen.py --top 10 --sort losers                    # top losers
python3 scripts/screen.py --min-volume 5e9 --top 20                 # liquidity filter
```

Output fields: market, price, change_pct, volume_24h_krw, high_52w, low_52w.
Default `--min-volume` 1e9 KRW — filters illiquid markets where spoofed moves
dominate.

## Deep dive on candidates (on request)

For the top candidates (default 5):

```bash
python3 scripts/upbit.py candles <market> --unit days --count 200 | python3 scripts/indicators.py
```

52-week position = (price − low_52w) / (high_52w − low_52w). Above 0.8 ⇒
"near high", below 0.2 ⇒ "near low".

## Interpretation rules

- Candidates up > 30% on the day are overheat-block gate subjects — no entry
  recommendation, observation only.
- Screening discovers; the final call belongs to the upbit-investor 8-stage
  pipeline.
- Cross-correlation (optional): `backtest.py correlate a.json b.json` between
  candidates — pairs with pearson > 0.8 are effectively one asset (no
  diversification) — warn.

## Output format

Table: market/price/day change/24h volume/52w position/one-line comment.
Deep-dive results in a separate section.
