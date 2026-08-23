#!/usr/bin/env python3
"""Upbit REST API wrapper — stdlib only.

Public calls need no keys. Private calls read UPBIT_ACCESS_KEY / UPBIT_SECRET_KEY.

Usage:
  upbit.py markets [--quote KRW]
  upbit.py ticker KRW-BTC [KRW-ETH ...]
  upbit.py candles KRW-BTC --unit minutes --minute 15 --count 200
  upbit.py candles KRW-BTC --unit days --count 200
  upbit.py orderbook KRW-BTC
  upbit.py trades KRW-BTC [--count 50]
  upbit.py accounts
  upbit.py chance KRW-BTC
  upbit.py order buy|sell KRW-BTC --price 10000            # market order (price=KRW amount)
  upbit.py order buy|sell KRW-BTC --price 50000000 --volume 0.001  # limit order
  upbit.py orders [--market KRW-BTC] [--state wait]
  upbit.py cancel <uuid>
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE = "https://api.upbit.com"
RETRY_STATUS = {429, 500, 502, 503}


def die(msg, code=1):
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(code)


def _jwt(query: dict | None) -> str:
    ak = os.environ.get("UPBIT_ACCESS_KEY", "")
    sk = os.environ.get("UPBIT_SECRET_KEY", "")
    if not ak or not sk:
        die("UPBIT_ACCESS_KEY / UPBIT_SECRET_KEY not set", 2)
    payload = {"access_key": ak, "nonce": str(uuid.uuid4())}
    if query:
        qs = urllib.parse.unquote(urllib.parse.urlencode(query))
        h = hashlib.sha512()
        h.update(qs.encode())
        payload["query_hash"] = h.hexdigest()
        payload["query_hash_alg"] = "SHA512"
    header = {"alg": "HS256", "typ": "JWT"}
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=")
    msg = enc(header) + b"." + enc(payload)
    sig = hmac.new(sk.encode(), msg, hashlib.sha256).digest()
    return (msg + b"." + base64.urlsafe_b64encode(sig).rstrip(b"=")).decode()


def call(path: str, method="GET", query: dict | None = None, body: dict | None = None, private=False):
    url = BASE + path
    headers = {"Accept": "application/json",
               "X-Upbit-Initiator": "upbit-investor-plugin/0.1.0"}
    data = None
    if query:
        url += "?" + urllib.parse.urlencode(query)
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if private:
        headers["Authorization"] = "Bearer " + _jwt(query if method == "GET" else None)
    last_err = None
    for attempt in range(3):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read().decode()
                # ponytail: no pagination loop — callers set --count within Upbit's 1-page cap
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            last_err = f"HTTP {e.code}: {detail}"
            if e.code in RETRY_STATUS and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            break
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = f"network: {e}"
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            break
    die(f"{method} {path} failed — {last_err}")


def cmd_markets(a):
    rows = call("/v1/market/all", query={"isDetails": "false"})
    if a.quote:
        rows = [r for r in rows if r["market"].startswith(a.quote + "-")]
    out = [{"market": r["market"], "korean": r.get("korean_name", ""), "english": r.get("english_name", "")} for r in rows]
    print(json.dumps(out, ensure_ascii=False))


def cmd_ticker(a):
    print(json.dumps(call("/v1/ticker", query={"markets": ",".join(a.markets)}), ensure_ascii=False))


def cmd_candles(a):
    unit = a.unit
    if unit == "minutes":
        path = f"/v1/candles/minutes/{a.minute}"
    elif unit == "weeks":
        path = "/v1/candles/weeks"
    elif unit == "months":
        path = "/v1/candles/months"
    else:
        path = f"/v1/candles/{unit}"
    rows = call(path, query={"market": a.market, "count": a.count})
    rows.reverse()  # oldest first — natural order for indicators
    print(json.dumps(rows, ensure_ascii=False))


def cmd_orderbook(a):
    print(json.dumps(call("/v1/orderbook", query={"markets": a.market}), ensure_ascii=False))


def cmd_trades(a):
    rows = call("/v1/trades/ticks", query={"market": a.market, "count": a.count})
    print(json.dumps(rows, ensure_ascii=False))


def cmd_accounts(a):
    print(json.dumps(call("/v1/accounts", private=True), ensure_ascii=False))


def cmd_chance(a):
    print(json.dumps(call("/v1/orders/chance", query={"market": a.market}, private=True), ensure_ascii=False))


def cmd_order(a):
    side = "bid" if a.side == "buy" else "ask"
    body = {"market": a.market, "side": side}
    if a.volume:  # limit order
        body.update({"volume": str(a.volume), "price": str(int(a.price)), "ord_type": "limit"})
    elif a.side == "buy":  # market buy: price = KRW amount to spend
        body.update({"price": str(int(a.price)), "ord_type": "price"})
    else:  # market sell: sell all of volume
        die("market sell needs --volume (coin amount to sell)")
    print(json.dumps(call("/v1/orders", method="POST", body=body, private=True), ensure_ascii=False))


def cmd_orders(a):
    q = {"state": a.state}
    if a.market:
        q["market"] = a.market
    print(json.dumps(call("/v1/orders", query=q, private=True), ensure_ascii=False))


def cmd_cancel(a):
    print(json.dumps(call("/v1/order", method="DELETE", query={"uuid": a.uuid}, private=True), ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Upbit API wrapper")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("markets"); s.add_argument("--quote", default=None); s.set_defaults(fn=cmd_markets)
    s = sub.add_parser("ticker"); s.add_argument("markets", nargs="+"); s.set_defaults(fn=cmd_ticker)
    s = sub.add_parser("candles")
    s.add_argument("market")
    s.add_argument("--unit", choices=["minutes", "days", "weeks", "months"], default="days")
    s.add_argument("--minute", type=int, choices=[1, 3, 5, 10, 15, 30, 60, 240], default=60)
    s.add_argument("--count", type=int, default=200)
    s.set_defaults(fn=cmd_candles)
    s = sub.add_parser("orderbook"); s.add_argument("market"); s.set_defaults(fn=cmd_orderbook)
    s = sub.add_parser("trades")
    s.add_argument("market"); s.add_argument("--count", type=int, default=50)
    s.set_defaults(fn=cmd_trades)
    s = sub.add_parser("accounts"); s.set_defaults(fn=cmd_accounts)
    s = sub.add_parser("chance"); s.add_argument("market"); s.set_defaults(fn=cmd_chance)
    s = sub.add_parser("order")
    s.add_argument("side", choices=["buy", "sell"]); s.add_argument("market")
    s.add_argument("--price", type=float, required=True)
    s.add_argument("--volume", type=float, default=None)
    s.set_defaults(fn=cmd_order)
    s = sub.add_parser("orders")
    s.add_argument("--market", default=None); s.add_argument("--state", default="wait")
    s.set_defaults(fn=cmd_orders)
    s = sub.add_parser("cancel"); s.add_argument("uuid"); s.set_defaults(fn=cmd_cancel)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
