#!/usr/bin/env python3
import json
import threading
import time
from datetime import UTC, datetime, timedelta

import ntplib
import pytz
import requests
from micommunity import APPLY_URL, STATE_URL, apply, get_headers, state

print("MiApplyEnhanced")
print("\nHow It Works: https://viewmd.github.io/MiForge/MiCommunityTool/refs/heads/main/miapply/README\n")

def retry(fn):
    try: return fn()
    except Exception: pass

def ping_once(session, headers):
    try:
        t0 = time.monotonic()
        session.get(STATE_URL, headers=headers, timeout=15)
        return (time.monotonic() - t0) * 1000.0
    except Exception: pass

def ask(prompt, default=None, minimum=1, options=None):
    raw = input(prompt).strip().lower()
    if not raw and default is not None: return default
    if options:
        for aliases, value in options:
            if raw in aliases: return value
    try:
        v = int(raw)
        if v >= minimum: return v
    except ValueError: pass

get_headers()
num_requests = ask("\nHow many requests? [4]: ", 4, 1)
mode = ask("Delay? [manual/auto] (auto): ", "auto", options=[({"m","manual"},"manual"),({"a","auto"},"auto")])
if mode == "manual":
    delay = ask("Delay in ms before 00:00 (GMT+8): ", minimum=0) / 1000.0
    when = None
    print(f"\n[manual] {delay*1000:.0f} ms | {num_requests} req")
else:
    when = ask("Ping now or later? Later = 20s before 0:00 GMT+8 [now/later] (later): ", "later", options=[({"n","now"},"now"),({"l","later"},"later")])
    print(f"\n[auto] {when} | {num_requests} req")

while True:
    session = requests.Session()
    headers = retry(lambda: get_headers(silent=True))
    status = retry(lambda: state(session.get(STATE_URL, headers=headers, timeout=15)))
    print(status.get('message'))
    if status.get('code') == 1: exit()

    tz = pytz.timezone("Asia/Shanghai")
    beijing_time = datetime.fromtimestamp(retry(lambda: ntplib.NTPClient().request("ntp1.aliyun.com", version=3)).tx_time, UTC).astimezone(tz)
    mono_ref = time.monotonic()
    midnight = (beijing_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    retry(lambda: session.get(STATE_URL, headers=headers, timeout=15))

    def take_ping_batch(label):
        print(f"\n[Ping ({label})...]")
        pings = [ping_once(session, headers) or 0.0 for _ in range(num_requests)]
        for i, p in enumerate(pings): print(f"  req {i+1}: {p:6.1f} ms")
        targets = [midnight - timedelta(seconds=p/1000.0) for p in pings]
        print()
        for i, t in enumerate(targets): print(f"  target {i+1}: {t.strftime('%H:%M:%S.%f')} (GMT+8)")
        print()
        return pings, targets

    if mode == "manual":
        pings, targets, ping_pending = None, [midnight - timedelta(seconds=delay)] * num_requests, False
        print(f"\n[Target] {targets[0].strftime('%H:%M:%S.%f')} (GMT+8)\n")
    elif when == "now":
        pings, targets = take_ping_batch("now"); ping_pending = False
    else:
        pings = targets = None; ping_pending = True
        print("\n[Waiting until ~20 s before midnight to measure ping...]\n")

    schedule = sorted(range(num_requests), key=lambda i: targets[i]) if targets else None
    warmed = fired = 0
    while True:
        now = beijing_time + timedelta(seconds=time.monotonic() - mono_ref)
        seconds_to_midnight = (midnight - now).total_seconds()
        if ping_pending and seconds_to_midnight <= 20:
            pings, targets = take_ping_batch("deferred"); schedule = sorted(range(num_requests), key=lambda i: targets[i]); ping_pending = False; continue
        if schedule is None: time.sleep(0.05); continue
        if not schedule: break
        idx = schedule[0]
        diff = (targets[idx] - now).total_seconds()
        if not warmed and diff <= 10:
            threading.Thread(target=lambda: session.get(STATE_URL, headers=headers, timeout=15), daemon=True).start()
            warmed = True
        if diff > 0:
            time.sleep(min(diff - 5, 30) if diff > 5 else 0.05 if diff > 1 else 0.0001)
            continue
        schedule.pop(0); fired += 1
        send_time = beijing_time + timedelta(seconds=time.monotonic() - mono_ref)
        print(f"[Req {fired}/{num_requests}] Sent at {send_time.strftime('%H:%M:%S.%f')} (GMT+8)")
        if mode == "auto": print(f"          (ping used: {pings[idx]:.1f} ms)")
        response = retry(lambda: session.post(APPLY_URL, headers=headers, json={"is_retry": True}, timeout=15))
        if response is None:
            print("          -> [no response — request failed]\n"); continue
        server_ts = response.json().get('ts', 0)
        if server_ts:
            print(f"          Server at {datetime.fromtimestamp(server_ts, UTC).astimezone(tz).strftime('%H:%M:%S.%f')} (GMT+8)")
        try: print(f"          Raw: {json.dumps(response.json(), ensure_ascii=False)}")
        except Exception: print(f"          Raw: {response.text!r}")
        print(f"          -> {apply(response).get('message')}\n")
    print(f"[Done — {num_requests} request(s) sent]\n")
    print("Now rush to press the `Bind Mi account` button regardless of the result!")
    print("If it didn't work, log out, log back in and try it again!")
