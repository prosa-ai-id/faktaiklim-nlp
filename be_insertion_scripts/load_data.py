import glob
import os
import re
from datetime import datetime

import pandas as pd
from utils import fix_set


def clean_title(text):
    """Keep only alphanumeric characters and join words"""
    # Convert to string in case we have non-string input
    text = str(text)
    # Keep only alphanumeric and spaces, convert to lowercase
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())
    # Join words with single spaces
    return " ".join(cleaned.split())


def convert_mongabay_date(date_str):
    """Convert date from '2 April 2024' to '2024-04-02 00:00:00'"""
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_str, "%d %B %Y")
        new_date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        # Convert to desired format
        return new_date_str
    except:
        return pd.NaT


def convert_science_feedback_date(date_str):
    date = date_str.strip()
    date += " 00:00:00"
    return date


def count_missed_title(di, all_mdf):
    """Count titles in di that are not found in all_mdf and save them to Excel"""
    # Create cleaned versions for comparison
    di["cleaned_title"] = di["Title"].str.lower().apply(clean_title)
    all_mdf["cleaned_title"] = all_mdf["Title"].str.lower().apply(clean_title)

    # Find missing titles
    found_titles = set(all_mdf["cleaned_title"])
    missing_mask = ~di["cleaned_title"].isin(found_titles)
    missing_df = di[missing_mask]

    # Save missing titles to Excel
    output_path = "xlsx/missing_titles.xlsx"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    missing_df.to_excel(output_path, index=False)

    # Remove temporary cleaning column
    di = di.drop("cleaned_title", axis=1, inplace=True)

    return len(missing_df), missing_df["Title"].tolist()


# Read the main topic file
# fname = "/home/miftah/Downloads/giz/finetune_huggingface/xlsx/Climate Worksheet_5_nov_2024.xlsx"
fname = "/home/miftah/Downloads/giz/modeling_scripts/raw_data/Climate Worksheet_5_nov_2024.xlsx"
df = pd.read_excel(fname, sheet_name="topic")
di = df.dropna(subset=["Title", "Topic"])
di["Topic"] = di["Topic"].apply(fix_set)
# print("Original topic dataframe:")
# print(di)

# Initialize list to store all matched dataframes
all_mdfs = []
title_counts = {}  # To store counts for each file

hoax_mapping = {
    "science_feedback": "HOAX",
    "antara": "FACT",
    "turnbackhoax": "HOAX",
    "mongabay": "FACT",
    "cekfakta_1-21639": "HOAX",
    "insideclimatenews": "FACT",
}

fnames = glob.glob("/home/miftah/Downloads/giz/raw_data/*.xlsx")
for fname in fnames:
    basename = os.path.basename(fname).split(".")[0]
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

    if "date" in ldf.columns:
        if basename == "science_feedback":
            ldf["date"] = ldf["date"].apply(convert_science_feedback_date)
        elif basename == "mongabay":
            ldf["date"] = ldf["date"].apply(convert_mongabay_date)
        elif basename == "insideclimatenews":
            ldf["date"] = ldf["date"].str.replace("T", " ")

        ldf["date"] = ldf["date"].ffill()

    # Clean and normalize titles
    di_titles = di["Title"].str.lower().apply(clean_title)
    ldf_titles = ldf[title_col].str.lower().apply(clean_title)

    # Create mask for matching titles
    mask = ldf_titles.isin(di_titles)

    # Create the merged dataframe
    mdf = ldf[mask]

    # Select only required columns from ldf (if they exist)
    required_cols = ["title", "content"]
    for col in ["url", "date"]:
        if col in mdf.columns:
            required_cols.append(col)
    mdf = mdf[required_cols]

    # Merge with topic information
    mdf = pd.merge(
        mdf, di[["Title", "Topic"]], left_on="title", right_on="Title", how="left"
    )

    mdf["classification"] = hoax_mapping[basename]

    # Store count of matches for this file
    title_counts[basename] = len(mdf)

    # Append to all_mdfs list
    all_mdfs.append(mdf)

    # print(f"Matched entries for {basename}:")
    # print(mdf)

# Concatenate all matched dataframes
all_mdf = pd.concat(all_mdfs, ignore_index=True)
all_mdf = all_mdf.dropna(subset=["Topic"])

# TODO: save all rows with missing titles to: xlsx.missing_titles.xlsx
# Count missed titles
missed_count, missed_titles = count_missed_title(di, all_mdf)

# Print detailed statistics
print("\n=== Detailed Statistics ===")
print(f"Total unique titles in topic file: {len(di)}")
print(f"Total titles found across all files: {len(all_mdf)}")
print(f"Missed titles count: {missed_count}")
print("\nMatches per file:")
for fname, count in title_counts.items():
    print(f"- {fname}: {count} matches")
# print("\nMissed titles:")
# for title in missed_titles:
#     print(f"- {title}")

all_mdf = all_mdf.drop(columns=["title", "cleaned_title"])
# all_mdf = all_mdf.rename(columns={"Title":"title", "Content": "content","Topic": "category"})
all_mdf = all_mdf.rename(columns={"Title": "title", "Topic": "category"})
total_nan_content = all_mdf["content"].isna().sum()
print(f"FOUND {total_nan_content} NAN CONTENT")
print(all_mdf[all_mdf["content"].isna()]["title"])

# Save results
output_path = "xlsx/be_data_14_nov_2024.xlsx"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
all_mdf.to_excel(output_path, index=False, sheet_name="BE_data")
print(f"\nResults saved to {output_path}")
