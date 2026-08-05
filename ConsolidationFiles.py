# -*- coding: utf-8 -*-
"""
Created on Mon May  5 16:13:12 2025

@author: Aparna Muraleedharan
"""

import pandas as pd

# 1. Read CSV files and parse Time
df1 = pd.read_csv(
    r"C:\Users\ge92wex\Downloads\Anomaly_2024\Experiment_2May2024_Column1.csv",
    parse_dates=["Time"],
    date_parser=lambda x: pd.to_datetime(x, format='%H:%M:%S')
).set_index("Time")

df2 = pd.read_csv(
    r"C:\Users\ge92wex\Downloads\Anomaly_2024\Experiment_2May2024_Column2.csv",
    parse_dates=["Time"],
    date_parser=lambda x: pd.to_datetime(x, format='%H:%M:%S')
).set_index("Time")


# Helper: resample mixed-type DataFrame
def resample_mixed(df, rule="30S"):
    # split numeric vs non-numeric
    num_cols = df.select_dtypes(include="number").columns
    obj_cols = df.columns.difference(num_cols)

    # numeric → mean, object → first in each bin
    df_num = df[num_cols].resample(rule).mean()
    df_obj = df[obj_cols].resample(rule).first()

    return pd.concat([df_num, df_obj], axis=1)


# 2. Resample each frame to 30-second bins, handling mixed types
df1_rs = resample_mixed(df1, "30S")
df2_rs = resample_mixed(df2, "30S")

# 3. Combine side-by-side
master_df = pd.concat([df1_rs, df2_rs], axis=1)

# 4. Fill gaps: interpolate numeric, forward-fill strings
master_df.interpolate(method="time", inplace=True)
master_df.ffill(inplace=True)


# 5. Remove stray second decimal in any string cell (e.g. "1.002.003" → "1.002003")
def fix_decimal_str(x):
    if isinstance(x, str) and x.count('.') == 2:
        a, b, c = x.split('.')
        return f"{a}.{b}{c}"
    return x

master_df = master_df.applymap(fix_decimal_str)


# 6. Export the combined result
print(master_df.head())
master_df.to_csv(
    r"C:\Users\ge92wex\Downloads\Anomaly_2024\ConsolidatedFiles\Experiment_2May2024.csv",
    index=True  # keeps Time as the first column
)

