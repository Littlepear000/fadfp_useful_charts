"""
Python Coding Sample (Quarterly Version)
Author: Xueqi (Shelley) Li

Description:
    This script demonstrates an end-to-end data analytics workflow using
    EMBIG sovereign spreads:

    1. Data retrieval (or local loading)
    2. Quarterly aggregation from daily data
    3. Filtering years (keeping 2008 and after)
    4. Reshaping to long format
    5. Metadata merging (IFS codes + group mapping)
    6. Computing group-level quarterly averages
    7. Visualizing results with clean and readable charts

    The script is written in a clean, modular, and interview-friendly style.
"""

# ============================================================
# 1. Import Packages
# ============================================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import imf_datatools
import pandaspro as cpd
from fadfpdata import cname_to_ifs


# ============================================================
# 2. Configuration
# ============================================================
update_date = "20251117"
download = 0   # switch to 1 if downloading from Bloomberg API

# Example group mapping dictionary (replace with real dictionary)
group_dict = {
    "AE": [111, 112, 113],
    "EM": [942, 950, 955],
    "LIC": [202, 203, 205]
}


# ============================================================
# 3. Data Download or Local Load
# ============================================================
if download == 1:
    ticker = cpd.pwread(r"EMBIG/Bloomberg EMBIG tickers.xlsx", sheet_name="filtered_list")[0]
    ticker_list = ticker["ticker"].values.tolist()
    ticker_dict = dict(zip(ticker["ticker"], ticker[["country", "ifscode"]].values.tolist()))

    embig_raw = imf_datatools.get_edi_bloomberg_data(ticker_list, "PX_LAST")
    embig_raw.columns = [col.replace("PX_LAST.D", "") for col in embig_raw.columns]

    rename_map = {ticker.upper(): values[0] for ticker, values in ticker_dict.items()}
    embig_raw.rename(columns=rename_map, inplace=True)

    embig_raw.to_csv(fr"EMBIG/EMBIG_raw_{update_date}.csv")

else:
    embig_raw = pd.read_csv(fr"EMBIG/EMBIG_raw_{update_date}.csv")
    embig_raw = embig_raw.set_index("dates")
    embig_raw.index = pd.to_datetime(embig_raw.index)


# ============================================================
# 4. Quarterly Aggregation + Filter 2008+
# ============================================================
# Resample to quarterly averages
quarterly = embig_raw.resample("Q").mean().reset_index()

# Reshape to long format
quarterly_long = quarterly.melt(
    id_vars="dates",
    value_name="embig",
    var_name="country"
)

# Add year and quarter
quarterly_long["year"] = quarterly_long["dates"].dt.year
quarterly_long["quarter"] = quarterly_long["dates"].dt.quarter

# Keep 2008+
quarterly_long = quarterly_long[quarterly_long["year"] >= 2008]


# ============================================================
# 5. Metadata Mapping (IFS + Group)
# ============================================================
# Map IFS codes
quarterly_long["ifscode"] = quarterly_long["country"].map(cname_to_ifs)
quarterly_long.loc[quarterly_long["country"] == "Global", "ifscode"] = 1


# Function to map ifscode → group
def map_group(ifscode, mapping):
    """
    Map an IFS code to its group based on a dictionary.
    Returns None if unmatched.
    """
    for group, values in mapping.items():
        if ifscode in values:
            return group
    return None


quarterly_long["group"] = quarterly_long["ifscode"].apply(
    lambda x: map_group(x, group_dict)
)


# ============================================================
# 6. Compute Group-Level Quarterly Averages
# ============================================================
group_quarterly_mean = (
    quarterly_long
    .groupby(["group", "year", "quarter"])["embig"]
    .mean()
    .reset_index()
)


# Pivot table (optional)
pivot_group_quarterly = (
    group_quarterly_mean
    .pivot(index=["year", "quarter"], columns="group", values="embig")
)


# ============================================================
# 7. Visualization Functions
# ============================================================
plt.style.use("seaborn-v0_8")


def plot_group_comparison(df, group_list):
    """
    Compare multiple groups' quarterly EMBIG trends.
    """
    plt.figure(figsize=(12, 6))

    for g in group_list:
        subset = df[df["group"] == g].sort_values(["year", "quarter"])
        subset["date_str"] = subset["year"].astype(str) + "Q" + subset["quarter"].astype(str)
        plt.plot(subset["date_str"], subset["embig"], linewidth=2, label=g)

    plt.title("Quarterly EMBIG Comparison Across Groups")
    plt.xlabel("Quarter")
    plt.ylabel("Spread")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_group_heatmap(pivot_df):
    """
    Plot heatmap of group-level quarterly averages.
    """
    plt.figure(figsize=(10, 6))
    sns.heatmap(pivot_df, cmap="viridis", annot=False)
    plt.title("Group-Level Quarterly EMBIG (2008+)")
    plt.xlabel("Group")
    plt.ylabel("Year-Quarter")
    plt.tight_layout()
    plt.show()


# ============================================================
# 8. Execution Block
# ============================================================
if __name__ == "__main__":

    # Compare 3 groups
    plot_group_comparison(group_quarterly_mean, ["AE", "EM", "LIC"])

    # Heatmap
    plot_group_heatmap(pivot_group_quarterly)

