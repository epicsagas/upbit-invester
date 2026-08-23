# upbit-investor

[English](./README_EN.md)

Upbit 코인 투자를 위한 멀티 에이전트 분석·매매 플러그인. Claude Code · Codex · agy · hermes 4종 호스트에서 동작한다. 의 심층 분석 파이프라인 (불/곰 디비트 → 판정 → 리스크 게이트 → 주문 제안)을 Upbit KRW 마켓에 이식했고, 시세 조회부터 스크리닝·백테스트·포트폴리오 관리까지 하나의 플러그인에 담았다.

**실제 주문은 절대 자동으로 나가지 않는다.** 모든 주문은 사용자 명시 확인 후에만 실행.

---

## 빠른 시작 (입문자용)

### 1단계 — 키 없이 시작 (시세만 보기)

설치 직후 아무 키 없이 바로 쓸 수 있는 것들:

```
"비트코인 지금 시세 어때?"
"KRW-BTC 호가창 보여줘"
"거래대금 많은 코인 Top 10 골라줘"
"KRW-BTC 기술적 지표 분석해줘"
```

### 2단계 — 종합 투자 분석

```
"KRW-BTC 분석해줘" ← 8단계 파이프라인 전체 실행
"이 코인 사도 될까?" ← 분석 + 진입 전략 제안
```

### 3단계 — 계좌 연동 (키 발급)

1. [Upbit → 내 정보 → API 관리](https://upbit.com/mypage/api)에서 **개인 API 키 발급** (보안: *조회* 권한만 허용해도 분석 전부 가능)
2. 환경변수 설정:

```bash
export UPBIT_ACCESS_KEY="..."
export UPBIT_SECRET_KEY="..."
```

3. 이제 가능:

```
"내 포트폴리오 점검해줘"
"KRW-BTC 10만원어치 매수해줘" ← 확인 절차를 거친 후에만 실행
```

> 💡 **입문자 권장**: API 키는 처음에 "조회 전용"으로 발급받아 쓰다가, 매매가 익숙해지면 그때 "주문" 권한을 추가하세요. 키는 절대 코드·채팅에 붙여넣지 말고 환경변수로만.

---

## 무엇을 해주나 (전체 지도)

```
┌─ 발견 ─────────────────────────────────────────────────┐
│ upbit-screen "뭐 좀 골라줘" — 거래대금/급등/급락 스크리닝 │
└──────────┬────────────────────────────────────────────┘
 ▼
┌─ 분석 ── upbit-investor (메인, 8단계 분석 파이프라인) ──┐
│ 1 스냅샷 수집 캔들·티커·호가·체결·지표·뉴스·과거결정 회상 │
│ 2 시장 분석가 추세/변동성/거래량 3-4문장 요약 │
│ 3 불 vs 곰 디비트 (라운드1 독립 논거) │
│ 4 불 vs 곰 디비트 (라운드2 상대 논거 직접 반박) │
│ 5 리서치 매니저 판정 JSON (rating/신뢰도/목표가) │
│ 6 리스크 매니저 6게이트 검사 + 포지션 크기 산출 │
│ 7 포트폴리오 매니저 과거 결정 회상 + 최종 판단 override │
│ 8 트레이더 주문 제안 JSON (진입가/손절/분할) │
│ │
│ 하위 스킬: upbit-market-data / upbit-technical │
└──────────┬────────────────────────────────────────┘
 ▼
┌─ 검증 ─────────────────────────────────────────────────┐
│ upbit-backtest 전략 과거 검증 (SMA크로스/RSI반전)·상관분석 │
└──────────┬────────────────────────────────────────────┘
 ▼
┌─ 실행·관리 ──────────────────────────────────────────┐
│ upbit-trade 확인 게이트 통과 후에만 실제 주문 │
│ upbit-portfolio 보유 점검·집중도 리스크·리밸런싱 권고 │
└────────────────────────────────────────────────────┘
```

각 분석 결론은 `~/.upbit-investor/decisions.jsonl`에 기록되어, 다음 분석 때
"지난번에 뭐라고 판단했었지"를 스스로 회상해 일관성을 유지한다.

## 안전장치

| 장치 | 내용 |
|------|------|
| 확인 게이트 | 주문 실행 전 항상 사용자에게 최종 확인 요청 |
| 리스크 6게이트 | 단일 코인 비중·총 투자 비중·과열 차단·당일 손실 한도 등 |
| 수수료 반영 | KRW 마켓 0.05% / BTC·USDT 마켓 0.25% (백테스트 양쪽 왕복 적용) |
| 킬스위치 | 당일 손실 한도 도달 시 이후 매수 제안 전면 차단 (hard) |
| 포지션 버림 | 예수금 초과 방지 — 수량 계산은 항상 내림 |
| 출금 미지원 | 출금 API는 플러그인에서 아예 다루지 않음 |

리스크 성향 프리셋: `conservative`(기본) / `momentum` / `long_term`.

## 설치

### Claude Code

```bash
claude plugin install epicsagas/upbit-investor
# 또는 로컬: claude plugin install /path/to/upbit-investor
```

### Codex

```bash
codex plugin add epicsagas/upbit-investor
```

### agy

`~/.agy/plugins/upbit-investor/`로 폴더 복사 후 재시작.

### hermes

`~/.hermes/plugins/upbit-investor/`로 폴더 복사 후 재시작.
> 설치 스캐너가 `AGENTS.md`을 CRITICAL persistence로 경고하면 `hermes plugins install
> --force`로 통과 (설정에서 `plugins.scan_on_install: false`로 끄는 방법도 있음).

## 구조

```
skills/ 7개 스킬 (SKILL.md가 진실 원천 — 모든 호스트가 여기를 봄)
 upbit-investor/ 메인 8단계 파이프라인 + references/(디비트·리스크·메모리 상세)
 upbit-market-data/ upbit-technical/ upbit-screen/
 upbit-backtest/ upbit-portfolio/ upbit-trade/
agents/ 7개 서브에이전트 (시장분석가·불·곰·리서치·리스크·포트폴리오·트레이더)
scripts/ stdlib-only Python — upbit.py(API) indicators.py history.py screen.py backtest.py
```

## 스크립트 직접 사용 (에이전트 없이)

```bash
python3 scripts/upbit.py ticker KRW-BTC
python3 scripts/upbit.py candles KRW-BTC --unit days --count 200 | python3 scripts/indicators.py
python3 scripts/history.py KRW-BTC --start 2024-08-01 # 전체 이력 (crix ZIP, 캐시)
python3 scripts/screen.py --top 10 --sort gainers
python3 scripts/backtest.py sma_cross --file /tmp/btc.json
python3 scripts/test_indicators.py # 지표 수학 자체검증
```

## 라이선스

MIT. 저작권 © 2026 epicsagas.

## 면책 조항 (Disclaimer)

본 플러그인("upbit-investor")은 소프트웨어 도구이며, 금융·투자 자문 서비스가
아니다. 어떠한 국가의 자본시장법·금융투자업 규제에 따른 투자자문업 또는
자산운용업에 해당하는 활동도 수행하지 않는다.

1. **투자 정보의 성격**: 이 플러그인이 제공하는 모든 분석, 지표 해석, 등급
 (Buy/Hold/Sell 등), 가격 목표, 주문 제안은 공개 데이터와 통계적 모형에서
 도출된 **참고 정보**일 뿐이며, 특정 코인의 매수·매도 권유, 수익 보장 또는
 손실 방지 약속이 아니다.
2. **투자 책임**: 암호화폐는 원금 손실 위험을 동반하는 고위험 자산이며,
 과거 수익률과 백테스트 결과는 미래 수익을 보장하지 않는다. 모든 투자
 판단과 그 결과에 대한 책임은 전적으로 사용자 본인에게 있다.
3. **데이터 정확성**: 시세·지표 데이터는 업비트 공개 API 기반으로 제공되며,
 전송 장애, 지연, 오류가 있을 수 있다. 주문 실행 전 사용자는 반드시
 거래소 공식 정보로 최종 확인해야 한다.
4. **소프트웨어 결함**: 본 소프트웨어는 "있는 그대로(AS IS)" 제공되며,
 상품성·특정 목적 적합성·비침해에 대한 묵시적 보증을 포함한 모든 보증을
 부인한다. 소프트웨어 결함·오작동·데이터 오류로 인한 직접·간접 손해에
 대해 개발자는 어떠한 책임도 지지 않는다.
5. **API 키 관리**: 업비트 API 키의 발급·보관·권한 설정은 사용자 책임이며,
 키 유출로 발생하는 모든 손실은 사용자가 부담한다. 주문 권한이 있는 키는
 필요한 경우에만 최소 범위로 사용하라.
6. **세금·법령 준수**: 암호화폐 거래에 따른 과세 및 관련 법령(특정금융정보법
 등)의 준수는 사용자의 의무이며, 본 플러그인은 세무·법률 자문을 제공하지
 않는다.

이 플러그인을 설치·사용하는 행위는 위 조항 전체에 동의한 것으로 간주된다.
