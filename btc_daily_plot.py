import os
from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

# --------------------
# Settings
# --------------------
TICKER = "BTC-USD"
PERIOD = "1y"
INTERVAL = "1d"
OUTDIR = "outputs"

os.makedirs(OUTDIR, exist_ok=True)

# Date-stamped filename
today = datetime.utcnow().strftime("%Y-%m-%d")
outfile = os.path.join(OUTDIR, f"BTC_25pct_{today}.png")
outfile_TODAY = os.path.join(OUTDIR, f"BTC_TODAY.png")

# --------------------
# Fetch data
# --------------------
df = yf.download(
    TICKER,
    period=PERIOD,
    interval=INTERVAL,
    auto_adjust=False,
    progress=False
)

if df is None or df.empty:
    raise RuntimeError("No data returned from Yahoo Finance.")

# Handle MultiIndex columns
if isinstance(df.columns, pd.MultiIndex):
    if ("Close", TICKER) in df.columns:
        close = df[("Close", TICKER)].dropna()
    else:
        close_cols = [c for c in df.columns if c[0] == "Close"]
        if not close_cols:
            raise RuntimeError("Could not find Close column.")
        close = df[close_cols[0]].dropna()
else:
    if "Close" not in df.columns:
        raise RuntimeError("Could not find Close column.")
    close = df["Close"].dropna()

close = close.astype(float)

# --------------------
# 52W stats
# --------------------
low_52w = float(close.min())
high_52w = float(close.max())
range_52w = high_52w - low_52w

lower_25 = low_52w + 0.25 * range_52w
upper_25 = high_52w - 0.25 * range_52w
current = float(close.iloc[-1])

# --------------------
# Plot
# --------------------
fig, ax = plt.subplots(figsize=(14, 7))
ax.plot(close.index, close.values, linewidth=2, color="black", label=f"{TICKER} Close")

ax.axhspan(low_52w, lower_25, alpha=0.10, label="Bottom 25% (52W)")
ax.axhspan(upper_25, high_52w, alpha=0.10, label="Top 25% (52W)")

for lvl, name in [
    (low_52w, "52W Low"),
    (lower_25, "Low+25%"),
    (upper_25, "High-25%"),
    (high_52w, "52W High"),
]:
    ax.axhline(lvl, linestyle="--", linewidth=1)
    ax.text(close.index[0], lvl, f"  {name}: ${lvl:.4f}", va="bottom", fontsize=9)

ax.set_title(f"{TICKER} — 1Y Price with 25% 52W Zones")
ax.set_xlabel("Date")
ax.set_ylabel("Price (USD)")
ax.grid(True, linestyle=":", alpha=0.7)
ax.legend(loc="best")

stats = (
    f"52W Low:   ${low_52w:.4f}\n"
    f"Lower 25%: ${lower_25:.4f}\n"
    f"Upper 25%: ${upper_25:.4f}\n"
    f"52W High:  ${high_52w:.4f}\n"
    f"Current:   ${current:.4f}"
)

fig.text(
    0.98, 0.95, stats,
    ha="right", va="top",
    fontsize=10,
    bbox=dict(boxstyle="round", alpha=0.15)
)

plt.tight_layout(rect=[0, 0, 0.88, 1])
plt.savefig(outfile, dpi=200, bbox_inches="tight")
plt.savefig(outfile_TODAY, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved {outfile}")
