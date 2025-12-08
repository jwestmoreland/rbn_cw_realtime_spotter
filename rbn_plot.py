# rbn_plot.py
# Large standalone green Gaussian plot with hover — tall peaks + 40m low freq filter

import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
from collections import deque
import queue

class RBNPlot:
    def __init__(self):
        self.freqs = deque(maxlen=1500)
        self.update_queue = queue.Queue()
        self.band_low = 7.0  # Default lower limit
        self.band_high = 7.3

        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_facecolor("#1a1a1a")
        self.ax.grid(alpha=0.3)
        self.canvas = self.fig.canvas
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)

        # Hover text
        self.cursor_text = self.ax.text(0, 0, "", color="yellow", fontsize=14, weight="bold",
                                        ha="center", va="top",
                                        bbox=dict(boxstyle="round,pad=0.5", facecolor="#000000", alpha=0.8))
        self.cursor_text.set_visible(False)

        plt.ion()
        plt.show()

        self.fig.canvas.manager.window.after(500, self.check_updates)

    def on_motion(self, event):
        if event.inaxes != self.ax:
            self.cursor_text.set_visible(False)
        else:
            freq = event.xdata
            if freq is not None:
                self.cursor_text.set_text(f"{freq:.3f} kHz")
                self.cursor_text.set_position((freq, self.ax.get_ylim()[1] * 0.92))
                self.cursor_text.set_visible(True)
        self.canvas.draw_idle()

    def set_band_limits(self, low, high):
        # Special rule for 40m: ignore anything below 6.95 MHz
        if abs(low - 7.0) < 0.1:  # 40m band
            low = 6.95
        self.band_low = low
        self.band_high = high
        self.update_queue.put(('limits', low, high))

    def add_freq(self, freq):
        # Filter out spots below band low edge (especially 40m junk)
        if freq >= self.band_low:
            self.update_queue.put(('freq', freq))
            
    def show_spotted_call(self, call):
        # Big spotted callsign overlay on the plot
        if not hasattr(self, 'spotted_text'):
            self.spotted_text = self.ax.text(0.5, 0.5, "", transform=self.ax.transAxes,
                                             fontsize=48, color="yellow", weight="bold",
                                             ha="center", va="center",
                                             bbox=dict(boxstyle="round,pad=1", facecolor="red", alpha=0.8))
        self.spotted_text.set_text(f"SPOTTED!\n{call}")
        self.spotted_text.set_visible(True)
        self.canvas.draw_idle()
        # Auto-hide after 5 seconds
        self.root.after(5000, lambda: self.spotted_text.set_visible(False) if hasattr(self, 'spotted_text') else None)
        self.canvas.draw_idle()
        
    def check_updates(self):
        while not self.update_queue.empty():
            cmd, *args = self.update_queue.get()
            if cmd == 'limits':
                low, high = args
                self.ax.set_xlim(low, high)
            elif cmd == 'freq':
                freq = args[0]
                self.freqs.append(freq)
                self.update_plot()
        self.fig.canvas.manager.window.after(500, self.check_updates)

    def update_plot(self):
        if len(self.freqs) > 30:
            kde = gaussian_kde(self.freqs, bw_method='scott')  # Tall, peaked hills like original
            low, high = self.band_low, self.band_high
            x = np.linspace(low, high, 1000)
            y = kde(x)
            self.ax.clear()
            self.ax.plot(x, y, color="#00ff00", lw=4)
            self.ax.fill_between(x, y, alpha=0.6, color="#008800")
            peak = x[np.argmax(y)]
            self.ax.axvline(peak, color="yellow", linestyle="--", lw=2)
            self.ax.set_title(f"RBN Live CW Activity — {len(self.freqs)} spots", color="white", fontsize=16)
            self.ax.set_xlabel("Frequency (kHz)", color="white")
            self.ax.set_ylabel("Activity", color="white")
            self.ax.grid(alpha=0.3)
            self.ax.set_facecolor("#1a1a1a")
            self.canvas.draw_idle()
            
  