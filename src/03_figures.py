"""
03_figures.py
Descriptive figures and summary tables for the UNGA ideal points analysis.

Input : data/processed/idealpoints_1991_2024.csv  (see src/02_clean.py)
Output: figures/fig1..fig5 *.png, output/summary_<year>.csv

Design: categorical colors follow a fixed validated order (blue, orange, aqua,
yellow, magenta) and are assigned per entity, never per rank. Every figure
carries a legend plus direct end-of-line labels, so identity never rests on
color alone.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed" / "idealpoints_1991_2024.csv"
FIG_DIR = ROOT / "figures"
OUT_DIR = ROOT / "output"

# --- design tokens (validated palette, light mode) ---------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
MAGENTA = "#e87ba4"

GROUP_COLOR = {
    "MENA": BLUE,
    "Western Europe & North America": ORANGE,
    "Latin America & Caribbean": AQUA,
    "Sub-Saharan Africa": YELLOW,
    "South & East Asia": MAGENTA,
}
GROUP_SHORT = {
    "MENA": "MENA",
    "Western Europe & North America": "W. Europe & N. America",
    "Latin America & Caribbean": "Latin America",
    "Sub-Saharan Africa": "Sub-Saharan Africa",
    "South & East Asia": "S. & E. Asia",
}
GROUP_ORDER = list(GROUP_COLOR)

# diverging ramp: blue <-> red with a neutral gray midpoint
DIVERGING = LinearSegmentedColormap.from_list(
    "blue_gray_red",
    ["#0d366b", "#2a78d6", "#9ec5f4", "#f0efec", "#f0a3a2", "#e34948", "#a32220"],
)

SOURCE = ("Source: Voeten (2025), \"UNGA Ideal Point Estimates, 1946-2025\", "
          "doi:10.7910/DVN/LEJUQZ; method: Bailey, Strezhnev & Voeten (2017).")

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "text.color": INK,
    "axes.labelcolor": INK2,
    "axes.edgecolor": AXIS,
    "axes.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "axes.axisbelow": True,
    "legend.frameon": False,
    "figure.dpi": 150,
    "savefig.dpi": 150,
})

Y_LABEL = "UNGA ideal point  (higher = closer to the United States)"
X_PAD = 8.5  # years of room reserved at the right for end-of-line labels


def add_title(fig, title: str, subtitle: str) -> None:
    fig.text(0.012, 0.975, title, fontsize=14, fontweight="bold", color=INK,
             va="top", ha="left")
    fig.text(0.012, 0.925, subtitle, fontsize=10, color=INK2, va="top", ha="left")


def add_source(fig) -> None:
    fig.text(0.012, 0.012, SOURCE, fontsize=7.5, color=MUTED, va="bottom", ha="left")


def bottom_legend(fig, handles, labels, ncol: int = 5) -> None:
    """One legend row below the plot, spanning the plot width."""
    fig.legend(handles, labels, loc="lower left",
               bbox_to_anchor=(0.075, 0.045, 0.915, 0.04),
               mode="expand", ncol=ncol, fontsize=9, handlelength=1.4,
               columnspacing=1.2, borderaxespad=0, frameon=False)


def label_endpoints(ax, ends, x_end, x_pad=X_PAD):
    """Direct-label line ends, nudged apart so labels never collide."""
    y0, y1 = ax.get_ylim()
    min_gap = (y1 - y0) * 0.062
    items = sorted(ends, key=lambda e: e[0])
    ys = [e[0] for e in items]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + min_gap)
    ax.set_xlim(right=x_end + x_pad)
    for (y_data, text, _color), y_lab in zip(items, ys):
        ax.annotate(text, xy=(x_end, y_data), xytext=(x_end + x_pad * 0.14, y_lab),
                    fontsize=9.5, color=INK, va="center", ha="left", annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.8,
                                    shrinkA=0, shrinkB=3))


def save(fig, name: str) -> None:
    fig.savefig(FIG_DIR / name)
    plt.close(fig)
    print(f"wrote figures/{name}")


# --- figures -----------------------------------------------------------------

def fig1_regional_trends(df: pd.DataFrame, end_year: int) -> None:
    mean = df.groupby(["year", "group"])["IdealPointFP"].mean().unstack("group")

    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    fig.subplots_adjust(left=0.075, right=0.99, top=0.85, bottom=0.20)

    ends = []
    for group in GROUP_ORDER:
        s = mean[group]
        ax.plot(s.index, s.values, color=GROUP_COLOR[group], lw=1.8, solid_capstyle="round")
        ax.plot(s.index[-1], s.values[-1], "o", color=GROUP_COLOR[group], ms=4.5)
        ends.append((s.values[-1], GROUP_SHORT[group], GROUP_COLOR[group]))

    ax.set_ylim(-1.45, 1.8)
    label_endpoints(ax, ends, end_year)

    ax.set_ylabel(Y_LABEL, fontsize=9.5)
    ax.set_xticks(range(1991, end_year + 1, 5))
    ax.grid(axis="x", visible=False)
    bottom_legend(fig,
                  [plt.Line2D([], [], color=GROUP_COLOR[g], lw=1.8) for g in GROUP_ORDER],
                  [GROUP_SHORT[g] for g in GROUP_ORDER])

    lowest = mean.idxmin(axis=1)
    n_lowest = int((lowest == "MENA").sum())
    add_title(fig, f"Alignment with the United States by region, 1991-{end_year}",
              f"Mean UNGA ideal point of each regional group. MENA (blue) has the lowest average "
              f"of the five in {n_lowest} of the {len(lowest)} years - yet its members are far "
              "from uniform (see fig. 3).")
    add_source(fig)
    save(fig, "fig1_regional_trends.png")


def fig2_great_powers(df: pd.DataFrame, end_year: int) -> None:
    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    fig.subplots_adjust(left=0.075, right=0.99, top=0.85, bottom=0.20)

    mena = df[df["group"] == "MENA"].groupby("year")["IdealPointFP"]
    m = mena.mean()
    ax.fill_between(m.index, mena.quantile(0.1).values, mena.quantile(0.9).values,
                    color=BLUE, alpha=0.13, lw=0)

    series = [
        (m, "MENA average", BLUE),
        (df[df.Countryname == "United States"].set_index("year")["IdealPointFP"], "United States", ORANGE),
        (df[df.Countryname == "Russia"].set_index("year")["IdealPointFP"], "Russia", AQUA),
        (df[df.Countryname == "China"].set_index("year")["IdealPointFP"], "China", YELLOW),
    ]
    ends = []
    for s, name, color in series:
        s = s[~s.index.duplicated()].sort_index()
        ax.plot(s.index, s.values, color=color, lw=1.8, solid_capstyle="round")
        ax.plot(s.index[-1], s.values[-1], "o", color=color, ms=4.5)
        ends.append((s.values[-1], name, color))

    ax.set_ylim(-2.15, 3.15)
    label_endpoints(ax, ends, end_year)

    ax.set_ylabel(Y_LABEL, fontsize=9.5)
    ax.set_xticks(range(1991, end_year + 1, 5))
    ax.grid(axis="x", visible=False)
    bottom_legend(fig, [plt.Line2D([], [], color=c, lw=1.8) for _, _, c in series],
                  [n for _, n, _ in series], ncol=4)

    add_title(fig, f"The Middle East between the great powers, 1991-{end_year}",
              "MENA average vs. the United States, Russia and China; shaded band = "
              "10th-90th percentile across the 21 MENA countries.")
    add_source(fig)
    save(fig, "fig2_great_powers.png")


def fig3_mena_heatmap(df: pd.DataFrame) -> None:
    mena = df[df["group"] == "MENA"]
    mat = mena.pivot(index="Countryname", columns="year", values="IdealPointFP")
    order = mat.iloc[:, -1].sort_values(ascending=False).index
    mat = mat.loc[order]

    vmax = float(max(abs(mat.min().min()), abs(mat.max().max())))

    fig, ax = plt.subplots(figsize=(11.5, 7))
    fig.subplots_adjust(left=0.155, right=0.955, top=0.86, bottom=0.10)

    im = ax.imshow(mat.values, aspect="auto", cmap=DIVERGING,
                   vmin=-vmax, vmax=vmax, interpolation="nearest")
    ax.set_facecolor(SURFACE)
    im.cmap.set_bad(SURFACE)

    ax.set_yticks(range(len(mat.index)), labels=mat.index, fontsize=8.5)
    xt = [i for i, y in enumerate(mat.columns) if y % 5 == 0]
    ax.set_xticks(xt, labels=[mat.columns[i] for i in xt])
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)

    cb = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.02)
    cb.set_label("ideal point  (red = closer to the US pole)", fontsize=9, color=INK2)
    cb.outline.set_visible(False)
    cb.ax.tick_params(color=MUTED, labelcolor=MUTED, labelsize=8.5)

    add_title(fig, f"Every MENA state in the UN General Assembly, 1991-{int(mat.columns[-1])}",
              "Rows sorted by the latest position. Blank cells = country not voting that year. "
              "Only Israel and Turkey ever appear on the US side of the scale.")
    add_source(fig)
    save(fig, "fig3_mena_heatmap.png")


def fig4_snapshot(df: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    year = int(df["year"].max())
    snap = df[df["year"] == year].sort_values("IdealPointFP").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(11.5, 5.6))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.83, bottom=0.15)

    x = list(range(len(snap)))
    others = snap["group"] != "MENA"
    ax.scatter([i for i, o in zip(x, others) if o],
               snap.loc[others, "IdealPointFP"], s=26, color=AXIS, lw=0, zorder=2)
    ax.scatter([i for i, o in zip(x, others) if not o],
               snap.loc[~others, "IdealPointFP"], s=42, color=BLUE, lw=0, zorder=3)

    for name in labels:
        row = snap[snap["Countryname"] == name]
        if row.empty:
            continue
        i, y = row.index[0], row["IdealPointFP"].iloc[0]
        is_mena = row["group"].iloc[0] == "MENA"
        ax.annotate(name, xy=(i, y), xytext=(i, y + (0.31 if is_mena else -0.36)),
                    fontsize=8.5, color=INK, ha="center",
                    va="bottom" if is_mena else "top", annotation_clip=False,
                    arrowprops=dict(arrowstyle="-", color=AXIS, lw=0.7, shrinkB=4))

    ax.set_xticks([])
    ax.set_xlabel(f"{len(snap)} UN member states, ranked by UNGA ideal point in {year}",
                  fontsize=9.5)
    ax.set_ylabel(Y_LABEL, fontsize=9.5)
    ax.set_xlim(-2, len(snap) + 12)
    ax.grid(axis="x", visible=False)
    ax.legend([plt.Line2D([], [], marker="o", ls="", color=BLUE, ms=6),
               plt.Line2D([], [], marker="o", ls="", color=AXIS, ms=6)],
              ["MENA countries", "all other UN members"], loc="lower right", fontsize=9)

    add_title(fig, f"Where the Middle East sits in the {year} UN General Assembly",
              "Each dot is one country. MENA states span nearly the whole scale - from Israel "
              "near the top to Syria at the very bottom - rather than forming a single bloc.")
    add_source(fig)
    save(fig, "fig4_snapshot.png")
    return snap


def fig5_dispersion(df: pd.DataFrame, end_year: int) -> None:
    sd = df.groupby(["year", "group"])["IdealPointFP"].std().unstack("group")

    fig, ax = plt.subplots(figsize=(10.5, 6.4))
    fig.subplots_adjust(left=0.075, right=0.99, top=0.85, bottom=0.20)

    ends = []
    for group in GROUP_ORDER:
        s = sd[group]
        ax.plot(s.index, s.values, color=GROUP_COLOR[group], lw=1.8, solid_capstyle="round")
        ax.plot(s.index[-1], s.values[-1], "o", color=GROUP_COLOR[group], ms=4.5)
        ends.append((s.values[-1], GROUP_SHORT[group], GROUP_COLOR[group]))

    ax.set_ylim(0, 1.05)
    label_endpoints(ax, ends, end_year)

    ax.set_ylabel("Standard deviation of ideal points within the group", fontsize=9.5)
    ax.set_xticks(range(1991, end_year + 1, 5))
    ax.grid(axis="x", visible=False)
    bottom_legend(fig,
                  [plt.Line2D([], [], color=GROUP_COLOR[g], lw=1.8) for g in GROUP_ORDER],
                  [GROUP_SHORT[g] for g in GROUP_ORDER])

    top = sd.idxmax(axis=1)
    n_top = int((top == "MENA").sum())
    add_title(fig, "Is the Middle East the most divided region?",
              f"Spread of ideal points within each regional group, 1991-{end_year}. MENA is the "
              f"most internally divided of the five groups in {n_top} of the {len(top)} years.")
    add_source(fig)
    save(fig, "fig5_dispersion.png")


def main() -> None:
    FIG_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(PROC, encoding="utf-8-sig")
    end_year = int(df["year"].max())

    fig1_regional_trends(df, end_year)
    fig2_great_powers(df, end_year)
    fig3_mena_heatmap(df)
    snap = fig4_snapshot(
        df,
        labels=["United States", "Russia", "China", "Israel", "Iran", "Syria",
                "Saudi Arabia", "Egypt", "Turkey", "India", "Brazil"],
    )
    fig5_dispersion(df, end_year)

    snap_out = snap[["Countryname", "iso3c", "group", "IdealPointFP", "NVotesFP"]].copy()
    snap_out.insert(0, "rank", range(1, len(snap_out) + 1))
    snap_out.to_csv(OUT_DIR / f"summary_{end_year}.csv", index=False)
    print(f"wrote output/summary_{end_year}.csv ({len(snap_out)} countries)")

    # numbers used in the README
    print("\n--- key numbers ---")
    for name in ["Israel", "Iran", "Saudi Arabia", "Egypt", "Turkey", "Syria"]:
        r = snap[snap.Countryname == name]
        if not r.empty:
            print(f"  {name:15s} ideal point {r.IdealPointFP.iloc[0]:+.2f}  "
                  f"rank {r.index[0] + 1}/{len(snap)}")
    sd = df.groupby(["year", "group"])["IdealPointFP"].std().unstack("group")
    top = sd.idxmax(axis=1)
    print(f"\nmost divided group in each year: MENA in {(top == 'MENA').sum()}/{len(top)} years")
    print("within-group SD, 1991 vs", end_year)
    print(sd.loc[[1991, end_year]].round(2).to_string())


if __name__ == "__main__":
    main()
