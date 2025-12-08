# rbn_gui.py
# Small GUI window for controls + SPOTTED alert

import asyncio
import re
import numpy as np
from scipy.stats import gaussian_kde
from datetime import datetime, timezone
import csv
from collections import deque
import tkinter as tk
from tkinter import ttk
import threading

from rbn_plot import RBNPlot  # Imports the plot class

BANDS = {
    '160m': (1800, 2000), '80m': (3500, 4000), '60m': (5350, 5370),
    '40m': (7000, 7300), '30m': (10100, 10150), '20m': (14000, 14350),
    '17m': (18068, 18168), '15m': (21000, 21450), '12m': (24890, 24990),
    '10m': (28000, 29700), '6m': (50000, 54000)
}

class RBNGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RBN Spotter Controls")
        self.root.geometry("400x300")
        self.root.configure(bg="#1a1a1a")

        self.plot = RBNPlot()  # Opens the large plot window
        self.running = False
        self.last_spot_times = {}

        # === Controls ===
        control_frame = tk.Frame(root, bg="#1a1a1a")
        control_frame.pack(pady=20, fill=tk.X, padx=20)

        tk.Label(control_frame, text="Callsign to alert:", fg="cyan", bg="#1a1a1a", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
        self.alert_call_var = tk.StringVar()
        tk.Entry(control_frame, textvariable=self.alert_call_var, width=15, font=("Arial", 12)).grid(row=0, column=1, padx=10)

        tk.Label(control_frame, text="Band:", fg="cyan", bg="#1a1a1a", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=10)
        self.band_var = tk.StringVar(value="40m")
        band_combo = ttk.Combobox(control_frame, textvariable=self.band_var, values=list(BANDS.keys()), width=12)
        band_combo.grid(row=1, column=1, padx=10, pady=10)

        button_frame = tk.Frame(root, bg="#1a1a1a")
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="START", command=self.start, bg="#00ff00", fg="black", font=("Arial", 14, "bold"), width=10).pack(side=tk.LEFT, padx=20)
        tk.Button(button_frame, text="STOP", command=self.stop, bg="#ff0000", fg="white", font=("Arial", 14, "bold"), width=10).pack(side=tk.LEFT, padx=20)

        # === SPOTTED Alert ===
        self.alert_label = tk.Label(root, text="", fg="yellow", bg="#1a1a1a", font=("Arial", 48, "bold"))
        self.alert_label.pack(expand=True)

    def flash_alert(self):
        self.alert_label.config(text="SPOTTED!", fg="red")
        self.root.after(300, lambda: self.alert_label.config(fg="yellow"))
        self.root.after(600, lambda: self.alert_label.config(fg="red"))
        self.root.after(900, lambda: self.alert_label.config(fg="yellow"))
        self.root.after(5000, lambda: self.alert_label.config(text=""))

    async def run_spotter(self):
        self.running = True
        band = self.band_var.get()
        low, high = BANDS[band]
        self.plot.set_band_limits(low, high)

        csv_file = f"rbn_spots_{band}_{self.alert_call_var.get() or 'all'}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}Z.csv"
        with open(csv_file, "w", newline="", encoding="utf-8") as logfile:  csv.writer(logfile).writerow(["timestamp", "freq_kHz", "callsign", "raw_line"])

        reader, writer = await asyncio.open_connection("rbn.telegraphy.de", 7000)
        writer.write(b"set/cw\r\n")
        writer.write(f"band {band}\r\n".encode())
        await writer.drain()

        while self.running:
            line = await reader.readline()
            if not line:
                break
            line_str = line.decode("ascii", errors="ignore").strip()
            if "DX de" not in line_str or "CW" not in line_str:
                continue

            m = re.search(r"(\d{4,5}\.\d+)", line_str)
            if not m:
                continue
            freq = float(m.group(1))
            if low <= freq <= high:
                spotted_call = line_str.split()[3].upper()

                # ALERT
                alert_call = self.alert_call_var.get().upper()
##                if alert_call and spotted_call == alert_call:
##                    self.root.after(0, self.flash_alert)
                    
                if alert_call and spotted_call == alert_call:
                    self.root.after(0, self.plot.show_spotted_call, spotted_call)  # Show on plot
                    self.root.after(0, self.flash_alert)  # Optional: keep control window flash too
                self.plot.add_freq(freq)

                # CSV
                timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
                with open(csv_file, "a", newline="", encoding="utf-8") as logfile:  csv.writer(logfile).writerow([timestamp, freq, spotted_call, line_str])

                # Suppress repeats
                key = (spotted_call, freq)
                now = datetime.now(timezone.utc).timestamp()
                if now - self.last_spot_times.get(key, 0) > 5:
                    self.last_spot_times[key] = now
                    print(f"{timestamp}  {freq:8.3f}  {spotted_call:12}  {line_str[-50:]}")

            await asyncio.sleep(0.05)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=asyncio.run, args=(self.run_spotter(),), daemon=True).start()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = RBNGUI(root)
    root.mainloop()