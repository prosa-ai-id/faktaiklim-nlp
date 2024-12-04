import glob
import os
from datetime import datetime

import pandas as pd


def convert_mongabay_date(date_str):
    """Convert date from '2 April 2024' to '2024-04-02 00:00:00'"""
    # Parse the date string
    date_obj = datetime.strptime(date_str, "%d %B %Y")
    # Convert to desired format
    return pd.Timestamp(date_obj)


fnames = glob.glob("/home/miftah/Downloads/giz/raw_data/*.xlsx")
for fname in fnames:
    basename = os.path.basename(fname).split(".")[0]
    if basename != "mongabay":
        continue
    ldf = pd.read_excel(fname, sheet_name=basename)
    print(f"\nProcessing {basename}..")
    # print(ldf)

    # Normalize column names
    ldf.columns = ldf.columns.str.lower()

    # Check for title column
    title_col = "title" if "title" in ldf.columns else None
    if title_col is None:
        print(f"Warning: No 'title' column found in {basename}")
        continue

    if basename == "mongabay" and "date" in ldf.columns:
        ldf["date"] = ldf["date"].apply(convert_mongabay_date)
    print(ldf)
