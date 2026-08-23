#!/usr/bin/env python3
"""Historical candles from crix-data.upbit.com ZIP archives — stdlib only.

The REST API caps candles at 200 bars; this fetches full daily/weekly/monthly
history as ZIP day-partitions (pattern from upbit-strategy-toolkit), converts
to the REST candle shape (so indicators.py/backtest.py accept it), oldest
first. Cached under ~/.upbit-investor/cache/.

Usage: history.py KRW-BTC [--start 2024-01-01] [--end 2026-08-23] [--tf day]
tf: day (default) | week (Mondays) | month
"""
import argparse
import datetime as dt
import io
import json
import os
import urllib.error
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

BASE = "https://crix-data.upbit.com"
CACHE = os.path.expanduser("~/.upbit-investor/cache")


def fetch_zip(url):
    req = urllib.request.Request(url, headers={"User-Agent": "upbit-investor-plugin/0.1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return zipfile.ZipFile(io.BytesIO(r.read()))
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            return None  # not-yet-published partition — normal at range edges
        raise


def to_candle(market, parts):
    """CSV row: date_time_utc,open,high,low,close,acc_trade_price,acc_trade_volume."""
    return {"market": market,
            "candle_date_time_kst": parts[0],
            "opening_price": float(parts[1]), "high_price": float(parts[2]),
            "low_price": float(parts[3]), "trade_price": float(parts[4]),
            "candle_acc_trade_volume": float(parts[6])}


def load_partition(market, tf, key):
    """One ZIP partition -> list of crix rows. key: YYYYMMDD (day/week) or YYYYMM (month)."""
    os.makedirs(CACHE, exist_ok=True)
    cache_path = os.path.join(CACHE, f"{market.replace('-', '_')}_{tf}_{key}.json")
    if os.path.exists(cache_path):
        return json.load(open(cache_path))
    url = f"{BASE}/candle/{market}/{'monthly' if tf == 'month' else 'daily'}/{tf}/{key[:4]}/{market}_candle-{tf}_{key}.zip"
    z = fetch_zip(url)
    if z is None:
        return []
    rows = []
    for name in z.namelist():
        if name.endswith(".csv"):
            text = z.read(name).decode("utf-8-sig")
            for line in text.splitlines()[1:]:  # header row
                parts = line.split(",")
                if len(parts) >= 7:
                    rows.append(parts[:7])
    with open(cache_path, "w") as f:
        json.dump(rows, f)
    return rows


def main():
    p = argparse.ArgumentParser(description="Upbit historical candles (crix ZIP archives)")
    p.add_argument("market")
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", default=None, help="YYYY-MM-DD (default today)")
    p.add_argument("--tf", choices=["day", "week", "month"], default="day")
    args = p.parse_args()

    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today()

    keys = []
    if args.tf == "month":
        d = start.replace(day=1)
        while d <= end:
            keys.append(d.strftime("%Y%m"))
            d = (d + dt.timedelta(days=32)).replace(day=1)
    else:
        step = dt.timedelta(days=7 if args.tf == "week" else 1)
        anchor = start
        if args.tf == "week":  # partitions keyed by Monday
            anchor = start - dt.timedelta(days=start.weekday())
        d = anchor
        while d <= end:
            keys.append(d.strftime("%Y%m%d"))
            d += step

    seen, candles = set(), []
    with ThreadPoolExecutor(max_workers=8) as pool:  # ponytail: fixed 8 threads; single-market tool
        for rows in pool.map(lambda k: load_partition(args.market, args.tf, k), keys):
            for parts in rows:
                if parts[0] in seen:
                    continue
                seen.add(parts[0])
                candles.append(to_candle(args.market, parts))
    candles.sort(key=lambda c: c["candle_date_time_kst"])
    print(json.dumps(candles, ensure_ascii=False))


if __name__ == "__main__":
    main()
