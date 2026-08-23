**[한국어](README.md)** | [English](README_EN.md)

<center><h1>upbit-investor</h1></center>

> 코인 투자 판단을 혼자 내리지 말고, 불리는 녀석과 곰되는 녀석을 붙여 싸게 하고 — 그 판정 위에 리스크 검사와 과거 판단 회상까지 얹어 보고서로 받기.

Claude Code, Codex, Antigravity, Hermes Agent 어디서든 동작하는 Upbit 코인 투자 플러그인입니다. 시세 조회, 스크리닝, 기술 지표, 백테스트, 포트폴리오 점검, 주문 실행까지 하나로 묶었고, 핵심인 종합 분석은 8단계 역할 분담 파이프라인(아래 표)으로 돌아갑니다. 매수·매도 주문은 절대 자동으로 나가지 않으며, 항상 마지막에 당신의 확인을 받습니다.

## 설치

```bash
# Claude Code
claude plugin marketplace add epicsagas/plugins
claude plugin install upbit-investor@epicsagas

# Codex
codex plugin marketplace add epicsagas/plugins
codex plugin add upbit-investor

# Antigravity
agy plugin install https://github.com/epicsagas/upbit-invester

# Hermes Agent — 설치 스캐너가 이 플러그인의 AGENTS.md 가이드를 CRITICAL
# "persistence"로 오탐합니다(에이전트 설정 파일 언급 전부를 잡는 휴리스틱).
# 설치 스캔을 잠시 끄고 설치한 뒤 다시 켜면 됩니다:
hermes config set plugins.scan_on_install false
hermes plugins install https://github.com/epicsagas/upbit-invester --enable
hermes config set plugins.scan_on_install true
hermes gateway restart
```

## 바로 시작

필요한 것: Python 3.10+, 에이전트 호스트 하나. 시세·분석엔 API 키가 필요 없고, 계좌 조회와 주문부터 키가 필요합니다.

```
You: "KRW-BTC 분석해줘"        → 8단계 파이프라인 전체 실행
You: "거래대금 많은 코인 골라줘" → 스크리닝 후 후보 요약
You: "KRW-BTC 백테스트해줘"     → 전략 성과 + 매수보유 벤치마크 비교
You: "비트코인 지금 시세 어때?"  → 티커/호가/캔들 팩트 정리
```

계좌 연동은 [Upbit → 내 정보 → API 관리](https://upbit.com/mypage/api)에서 키를 발급받아 환경변수로 등록하면 끝납니다. 처음엔 조회 권한만 허용하는 걸 권합니다 — 분석은 전부 되고, 주문 권한은 나중에 필요할 때 추가하면 됩니다. 키는 절대 채팅이나 코드에 붙여넣지 말고 환경변수로만:

```bash
export UPBIT_ACCESS_KEY="..."
export UPBIT_SECRET_KEY="..."
```

## 어떻게 돌아가나

"KRW-BTC 분석해줘" 한 마디면 아래 8단계가 순서대로 돌면서 각 단계의 산출물이 다음 단계의 입력이 됩니다. 투표가 아니라 계층 판정 구조라서 근거가 아래로 누적됩니다.

| | 단계 | 하는 일 |
|--|------|--------|
| 📸 | 스냅샷 | 일봉·분봉 캔들, 티커, 호가, 체결, 지표 JSON, 최근 뉴스, 과거 판단 회상까지 한 덩어리로 수집 |
| 👁 | 시장 분석가 | 추세·변동성·거래량 이상을 몇 문장으로 요약 |
| 🐂 | 불 리서처 | 매수 근거를 스냅샷 수치와 함께 주장 (라운드 1) |
| 🐻 | 곰 리서처 | 매도·보류 근거를 독립적으로 주장 (라운드 1) |
| ⚔️ | 디비트 라운드 2 | 서로의 라운드 1 논거를 직접 반박 |
| 🧑‍⚖️ | 리서치 매니저 | 디비트를 증거 품질로 판정 — 등급·신뢰도·목표가 JSON |
| 🛡 | 리스크 매니저 | 6개 리스크 게이트 검사 + 포지션 크기 산출 |
| 📊 | 포트폴리오 매니저 | 과거 판단과 대조해 최종 판단 (override 가능) |
| 📝 | 트레이더 | 진입가·손절가·분할 매수까지 담은 주문 제안 — **제안만** |

최종 보고서를 받으면 판단이 `~/.upbit-investor/decisions.jsonl`에 한 줄 기록되고, 다음 분석 때 같은 코인의 이전 판단이 회상됩니다. 지난번에 뭐라고 판단했었는지, 방향을 뒤집은 건 아닌지 스스로 대조해서 일관성을 유지합니다.

주변 스킬: `upbit-market-data`(시세 팩트), `upbit-technical`(지표 판독), `upbit-screen`(스크리닝), `upbit-backtest`(전략 검증·상관분석), `upbit-portfolio`(보유 점검), `upbit-trade`(확인 게이트 통과 후 주문 실행).

## 안전장치

| 장치 | 내용 |
|------|------|
| 확인 게이트 | 주문 실행 전 항상 사용자에게 최종 확인 요청 |
| 리스크 6게이트 | 단일 코인 비중·총 투자 비중·과열 차단·주문 빈도·당일 손실 한도 |
| 킬스위치 | 당일 손실 한도 도달 시 이후 매수 제안 전면 차단 (hard) |
| 포지션 버림 | 예수금 초과 방지 — 수량 계산은 항상 내림 |
| 수수료 반영 | KRW 마켓 0.05% / BTC·USDT 마켓 0.25%, 백테스트 양쪽 왕복 적용 |
| 출금 미지원 | 출금 API는 플러그인에서 아예 다루지 않음 |

리스크 성향 프리셋: `conservative`(기본) / `momentum` / `long_term`.

## FAQ

<details>
<summary>API 키 없이도 써볼 수 있나요?</summary>

네. 시세·캔들·호가·체결·스크리닝·지표·백테스트는 전부 공개 API라 키가 필요 없습니다. 계좌 조회와 주문부터 키가 필요하고, 키가 없으면 읽기 전용 분석만 진행합니다.

</details>

<details>
<summary>자동 매매 되나요?</summary>

안 됩니다. 파이프라인은 주문까지 "제안"할 뿐이고, 실행은 upbit-trade 스킬의 확인 게이트에서 당신이 "예"라고 답했을 때만 이뤄집니다. 출금은 애초에 지원하지 않습니다.

</details>

<details>
<summary>백테스트는 데이터를 얼마나 쓰나요?</summary>

REST API로는 최근 200봉, `scripts/history.py`로 crix ZIP 아카이브에서 일·주·월 전체 이력을 가져옵니다(로컬 캐시). 1~2년 이상 구간으로 돌리는 걸 권합니다 — 거래 수가 적으면 통계가 무의미해집니다.

</details>

<details>
<summary>"당일 손실 한도 초과"라며 매수가 막혔어요.</summary>

킬스위치(6번 게이트, hard)입니다. conservative 프리셋 기준 당일 손실이 예수금 대비 −3%를 넘으면 이후 매수 제안이 전부 차단됩니다. 프리셋을 바꾸거나 다음 날까지 기다리는 게 정상 대응입니다.

</details>

<details>
<summary>지표가 이상하게 나오는 것 같아요.</summary>

`python3 scripts/test_indicators.py`로 지표 수학 자체검증을 돌려보세요. 통과하면 계산은 정상이고 해석 기준은 `upbit-technical` 스킬의 판독표를 따릅니다.

</details>

## 스크립트 직접 사용 (에이전트 없이)

```bash
python3 scripts/upbit.py ticker KRW-BTC
python3 scripts/upbit.py candles KRW-BTC --unit days --count 200 | python3 scripts/indicators.py
python3 scripts/history.py KRW-BTC --start 2024-08-01   # 전체 이력 (crix ZIP, 캐시)
python3 scripts/screen.py --top 10 --sort gainers
python3 scripts/backtest.py sma_cross --file /tmp/btc.json
python3 scripts/test_indicators.py   # 지표 수학 자체검증
```

전부 Python 표준 라이브러리만 사용 — 의존성 설치가 없습니다.

## 라이선스

MIT. 저작권 © 2026 epicsagas.

## 면책 조항 (Disclaimer)

본 플러그인("upbit-investor")은 소프트웨어 도구이며, 금융·투자 자문 서비스가 아니다. 어떠한 국가의 자본시장법·금융투자업 규제에 따른 투자자문업 또는 자산운용업에 해당하는 활동도 수행하지 않는다.

1. **투자 정보의 성격**: 이 플러그인이 제공하는 모든 분석, 지표 해석, 등급(Buy/Hold/Sell 등), 가격 목표, 주문 제안은 공개 데이터와 통계적 모형에서 도출된 **참고 정보**일 뿐이며, 특정 코인의 매수·매도 권유, 수익 보장 또는 손실 방지 약속이 아니다.
2. **투자 책임**: 암호화폐는 원금 손실 위험을 동반하는 고위험 자산이며, 과거 수익률과 백테스트 결과는 미래 수익을 보장하지 않는다. 모든 투자 판단과 그 결과에 대한 책임은 전적으로 사용자 본인에게 있다.
3. **데이터 정확성**: 시세·지표 데이터는 업비트 공개 API 기반으로 제공되며, 전송 장애, 지연, 오류가 있을 수 있다. 주문 실행 전 사용자는 반드시 거래소 공식 정보로 최종 확인해야 한다.
4. **소프트웨어 결함**: 본 소프트웨어는 "있는 그대로(AS IS)" 제공되며, 상품성·특정 목적 적합성·비침해에 대한 묵시적 보증을 포함한 모든 보증을 부인한다. 소프트웨어 결함·오작동·데이터 오류로 인한 직접·간접 손해에 대해 개발자는 어떠한 책임도 지지 않는다.
5. **API 키 관리**: 업비트 API 키의 발급·보관·권한 설정은 사용자 책임이며, 키 유출로 발생하는 모든 손실은 사용자가 부담한다. 주문 권한이 있는 키는 필요한 경우에만 최소 범위로 사용하라.
6. **세금·법령 준수**: 암호화폐 거래에 따른 과세 및 관련 법령(특정금융정보법 등)의 준수는 사용자의 의무이며, 본 플러그인은 세무·법률 자문을 제공하지 않는다.

이 플러그인을 설치·사용하는 행위는 위 조항 전체에 동의한 것으로 간주된다.
