"""
02_clean.py
Load the raw UNGA ideal point estimates, keep the post-Cold War period
(1991-2025), and attach a regional group label to each country-year.

Input : data/raw/IdealPointEstimates_1946-2025.csv   (see src/01_download.py)
Output: data/processed/idealpoints_1991_2025.csv

Group definitions follow conventional World Bank / UN regional groupings;
they are analytical choices, not facts about the world. Adjust freely.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "IdealPointEstimates_1946-2025.csv"
OUT_DIR = ROOT / "data" / "processed"

START_YEAR = 1991  # post-Cold War: avoids the German/Yemeni unification breaks
END_YEAR = 2024    # 2025 estimates are excluded on purpose: the data provider warns
                   # that 2024-25 voting turned two-dimensional and the 2025 file
                   # merges far more votes than a normal session (191 vs ~100),
                   # which makes the single-dimension estimates non-comparable.

# --- Regional groups used in the descriptive figures -------------------------
MENA = [
    "Algeria", "Bahrain", "Egypt", "Iran", "Iraq", "Israel", "Jordan",
    "Kuwait", "Lebanon", "Libya", "Mauritania", "Morocco", "Oman", "Qatar",
    "Saudi Arabia", "Sudan", "Syria", "Tunisia", "Turkey",
    "United Arab Emirates", "Yemen",
]

WEST = [
    "Australia", "Austria", "Belgium", "Canada", "Denmark", "Finland",
    "France", "Germany", "Greece", "Iceland", "Ireland", "Italy",
    "Luxembourg", "Netherlands", "New Zealand", "Norway", "Portugal",
    "Spain", "Sweden", "Switzerland", "United Kingdom", "United States",
]

LATIN_AMERICA = [
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Costa Rica",
    "Cuba", "Dominican Republic", "Ecuador", "El Salvador", "Guatemala",
    "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Paraguay",
    "Peru", "Trinidad & Tobago", "Uruguay", "Venezuela",
]

SUB_SAHARAN_AFRICA = [
    "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde",
    "Chad", "Comoros", "Congo - Brazzaville", "Congo - Kinshasa",
    "Côte d’Ivoire", "Djibouti", "Eritrea", "Eswatini", "Ethiopia", "Gabon",
    "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Kenya", "Lesotho",
    "Liberia", "Madagascar", "Malawi", "Mali", "Mauritius", "Mozambique",
    "Namibia", "Niger", "Nigeria", "Rwanda", "Senegal", "Seychelles",
    "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Tanzania",
    "Togo", "Uganda", "Zambia", "Zimbabwe",
]

SOUTH_EAST_ASIA = [
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Indonesia", "Japan",
    "Laos", "Malaysia", "Maldives", "Mongolia", "Myanmar (Burma)", "Nepal",
    "Pakistan", "Philippines", "Singapore", "South Korea", "Sri Lanka",
    "Thailand", "Timor-Leste", "Vietnam",
]

GROUPS = {
    "MENA": MENA,
    "Western Europe & North America": WEST,
    "Latin America & Caribbean": LATIN_AMERICA,
    "Sub-Saharan Africa": SUB_SAHARAN_AFRICA,
    "South & East Asia": SOUTH_EAST_ASIA,
}


def build_group_map() -> dict:
    mapping = {}
    for group, countries in GROUPS.items():
        for c in countries:
            mapping[c] = group
    return mapping


def main() -> None:
    df = pd.read_csv(RAW, encoding="utf-8-sig")

    # First column of the Dataverse export is an unnamed row index
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")])

    df = df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)].copy()
    df["group"] = df["Countryname"].map(build_group_map()).fillna("Other")

    keep = [
        "ccode", "iso3c", "Countryname", "year", "session", "NVotesFP",
        "IdealPointFP", "Q5%FP", "Q10%FP", "Q50%FP", "Q90%FP", "Q95%FP",
        "group",
    ]
    df = df[keep].sort_values(["Countryname", "year"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"idealpoints_{START_YEAR}_{END_YEAR}.csv"
    df.to_csv(out, index=False)

    print(f"wrote {out.relative_to(ROOT)}")
    print(f"  {len(df):,} country-year observations, {df['year'].min()}-{df['year'].max()}")
    print(f"  {df['Countryname'].nunique()} countries")
    print(df.groupby("group")["Countryname"].nunique().sort_values(ascending=False).to_string())


if __name__ == "__main__":
    main()
