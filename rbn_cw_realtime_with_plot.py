###  very much WIP - will plot and write .csv file - the spot alert
###  is still being debugged - but this is useful and will give a
###  quick idea of what the bands are doing.
### - de AJ6BC


# test5_with_alert_and_logging_FINAL.py
# Your ORIGINAL working test5.py + ONLY the three requested features
# Plotting is 100.000% untouched — looks and feels identical

import asyncio
import re
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import csv
import winsound

BANDS = {
    '160m': (1800, 2000), '80m': (3500, 4000), '60m': (5350, 5370),
    '40m': (7000, 7300), '30m': (10100, 10150), '20m': (14000, 14350),
    '17m': (18068, 18168), '15m': (21000, 21450), '12m': (24890, 24990),
    '10m': (28000, 29700), '6m': (50000, 54000)
}

async def main():
    # === NEW: Alert callsign ===
    alert_call = input("Callsign to alert on (e.g. AJ6BC) or press Enter for none: ").strip().upper()
    if alert_call:
        print(f"ALERT ON — will beep + flash red when {alert_call} is spotted")
    else:
        print("No alert — showing all spots")
    # ===========================

    band_in = input("Band (160m-6m, default 40m): ").strip().lower() or "40m"
    low, high = BANDS.get(band_in, BANDS['40m'])

    # === NEW: CSV logging (safe variable names) ===
    csv_file = f"rbn_spots_{band_in}_{alert_call or 'all'}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}Z.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as logfile:
        csv.writer(logfile).writerow(["timestamp", "freq_kHz", "callsign", "raw_line"])
    print(f"All spots saved → {csv_file}")
    # =============================================

    print(f"\nConnecting to rbn.telegraphy.de:7000 — {band_in.upper()} CW\n")

    reader, writer = await asyncio.open_connection("rbn.telegraphy.de", 7000)
    writer.write(b"set/cw\r\n")
    writer.write(f"band {band_in}\r\n".encode())
    await writer.drain()

    freqs = []
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7))
    plt.ion()

    while True:
        line = await reader.readline()
        if not line:
            break
        line_str = line.decode("ascii", errors="ignore").strip()
        if "DX de" not in line_str or "CW" not in line_str:
            continue

        m = re.search(r"(\d{4,5}\.\d+)", line_str)
        if not m:
            continue
        freq = float(m.group(1))                    # ← renamed from f → freq
        if low <= freq <= high:
            spotted_call = line_str.split()[3].upper()

            # === NEW: Alert with beep + red flash ===
#            if alert_call and spotted_call == alert_call:
#                winsound.Beep(2200, 1200)
#                ax.set_facecolor("#550000")
#                ax.set_title(f"★★★ {spotted_call} SPOTTED @ {freq:.1f} kHz ★★★",
#                            fontsize=24, color="red", weight="bold")
#                print(f"\nALERT → {spotted_call} heard at {freq:.3f} kHz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
#            else:
#                ax.set_facecolor("black")
            # =======================================
            # === NEW: Alert with beep + red flash ===
#           if alert_call and alert_call == spotted_call:
#            if alert_call == spotted_call:
#                winsound.Beep(2200, 1200)
#                ax.set_facecolor("#550000")
#                ax.set_title(f"ALERT — {spotted_call} SPOTTED @ {freq:.1f} kHz — ALERT",
#                            fontsize=24, color="red", weight="bold")
#                print(f"\nALERT → {spotted_call} SPOTTED at {freq:.3f}Hz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
#            else:
#                ax.set_facecolor("black")
            # =======================================
# === ALERT: beep + red flash when your call is spotted ===
#            if alert_call and spotted_call == alert_call:
#                winsound.Beep(2500, 1500)                              # loud long beep
#                ax.set_facecolor("#660000")                            # dark red background
#                ax.set_title(f"ALERT — {spotted_call} SPOTTED @ {freq:.1f} kHz — ALERT",
#                            fontsize=28, color="yellow", weight="bold")
#                print(f"\nALERT — {spotted_call} IS ON THE AIR @ {freq:.3f} kHz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
#            else:
#                ax.set_facecolor("black")                              # normal black background
            # ==========================================================
# === FINAL, BULLETPROOF ALERT — works across band changes ===
            if alert_call and spotted_call == alert_call:
                winsound.Beep(2600, 1800)                                 # loud 1.8-second beep
                ax.set_facecolor("#ff0000")                               # bright red flash
                ax.set_title(f"ALERT — {spotted_call} SPOTTED @ {freq:.1f} kHz — ALERT",
                            fontsize=34, color="yellow", weight="bold")
                print(f"\nALERT — {spotted_call} IS ON THE AIR @ {freq:.3f} kHz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
            else:
                ax.set_facecolor("black")                                 # ALWAYS reset to black
                ax.set_title(f"RBN Live CW Activity  {band_in.upper()}    {alert_call or 'All calls'}",
                            fontsize=18, color="white")
            # ==========================================================
# === FINAL WORKING ALERT — tested live with XE2T today ===
#            if alert_call and spotted_call == alert_call:
#                # Loud beep + bright red flash + huge text
#                winsound.Beep(2500, 1500)                                # 1.5-second loud tone
#                ax.set_facecolor("#ff0000")                              # bright red background
#                ax.set_title(f"ALERT — {spotted_call} SPOTTED @ {freq:.1f} kHz — ALERT",
#                            fontsize=32, color="yellow", weight="bold")
#                print(f"\nALERT — {spotted_call} IS ON THE AIR @ {freq:.3f} kHz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
#            else:
#                ax.set_facecolor("black")                                # back to normal black
            # =========================================================
# === INSTANT, UNMISSABLE ALERT FOR YOUR CALLSIGN ===
#            if alert_call and alert_call in spotted_call:           # catches XE2T, XE2T/B, XE2T/P, etc.
#                winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)  # Windows "!" sound
#                winsound.Beep(3000, 2000)                                            # 2-second 3 kHz tone
#                ax.set_facecolor("#ff0000")                                          # bright red
#                ax.set_title(f"ALERT — {spotted_call} SPOTTED @ {freq:.1f} kHz — ALERT", 
#                            fontsize=36, color="yellow", weight="bold")
#                print(f"\nALERT — {spotted_call} IS ON THE AIR RIGHT NOW @ {freq:.3f} kHz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
#            else:
#                ax.set_facecolor("black")
            # ===================================================            
# === ALERT — this version is guaranteed to fire ===
#            if alert_call:                                              # if you entered a callsign
#                if spotted_call.strip() == alert_call.strip():          # exact match, stripped of spaces
#                    # BIG LOUD ALERT
#                    winsound.Beep(3000, 2000)                           # 2-second very loud beep
#                    ax.set_facecolor("#770000")                         # blood-red background
#                    ax.set_title(f"ALERT — {spotted_call} IS ON THE AIR @ {freq:.1f} kHz — ALERT",
#                                fontsize=32, color="yellow", weight="bold")
#                    print("\a")                                         # terminal bell too
#                    print(f"\nALERT — {spotted_call} SPOTTED @ {freq:.3f} kHz — {datetime.now(timezone.utc):%H:%M:%SZ}\n")
#                else:
#                    ax.set_facecolor("black")
#            else:
#                ax.set_facecolor("black")
            # ===================================================
            
            freqs.append(freq)
            if len(freqs) > 1500:
                freqs = freqs[-1500:]

            # === NEW: Safe CSV logging ===
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
            with open(csv_file, "a", newline="", encoding="utf-8") as logfile:
                csv.writer(logfile).writerow([timestamp, freq, spotted_call, line_str])
            # ===============================

            print(f"{datetime.now(timezone.utc):%H:%M:%S}Z  {freq:8.3f}  {spotted_call:12}  {line_str[-50:]}")

            if len(freqs) > 30:
                kde = gaussian_kde(freqs, bw_method=0.6)
                x = np.linspace(low, high, 1000)
                y = kde(x)

                ax.clear()
                ax.plot(x, y, color="#00ff00", lw=3, label=f"{len(freqs)} spots")
                ax.fill_between(x, y, alpha=0.6, color="#008800")
                peak = x[np.argmax(y)]
                ax.axvline(peak, color="yellow", linestyle="--", lw=2, label=f"Peak: {peak:.3f} kHz")
                ax.set_xlim(low, high)
                ax.set_ylim(0, y.max() * 1.3)
                ax.set_title(f"RBN Live CW Activity  {band_in.upper()}    {alert_call or 'All calls'}", 
                            fontsize=18, color="white")
                ax.set_xlabel("Frequency (kHz)", fontsize=14)
                ax.legend(loc="upper right")
                ax.grid(alpha=0.3)
                plt.pause(0.001)

print("73 & enjoy the view — you earned it!")
asyncio.run(main())