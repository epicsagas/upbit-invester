#!/usr/bin/env python3
"""Screen KRW markets by volume/change extremes — stdlib only.

Usage: screen.py [--top 10] [--min-volume 1e9] [--sort volume|gainers|losers]
"""
import argparse
import json
import sys
import urllib.request


def get(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode())


def main():
    p = argparse.ArgumentParser(description="Upbit KRW market screener")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--min-volume", type=float, default=1e9, help="min 24h KRW volume (default 1e9)")
    p.add_argument("--sort", choices=["volume", "gainers", "losers"], default="volume")
    args = p.parse_args()

    markets = [m["market"] for m in get("https://api.upbit.com/v1/market/all?isDetails=false")
               if m["market"].startswith("KRW-")]
    rows = []
    for i in range(0, len(markets), 100):  # ticker endpoint caps ~100 ids? Upbit allows all, chunk for safety
        chunk = ",".join(markets[i:i + 100])
        rows += get("https://api.upbit.com/v1/ticker?markets=" + chunk)

    rows = [r for r in rows if r.get("acc_trade_price_24h", 0) >= args.min_volume]
    key = {"volume": lambda r: -r["acc_trade_price_24h"],
           "gainers": lambda r: -r["signed_change_rate"],
           "losers": lambda r: r["signed_change_rate"]}[args.sort]
    rows.sort(key=key)

    out = [{"market": r["market"], "price": r["trade_price"],
            "change_pct": round(r["signed_change_rate"] * 100, 2),
            "volume_24h_krw": int(r["acc_trade_price_24h"]),
            "high_52w": r.get("highest_52_week_price"), "low_52w": r.get("lowest_52_week_price")}
           for r in rows[:args.top]]
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
