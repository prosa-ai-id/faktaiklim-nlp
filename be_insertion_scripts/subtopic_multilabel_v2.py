# loading raw subtopic data to multilabel dataset, version 2
# added unknown (empty label) processing

import json
import os
import pickle
import random
from collections import Counter

import numpy as np
import pandas as pd
from utils import (
    fix_set,
    get_all_multilabel_class,
    get_single_label,
    remove_small_topic,
    save_to_txt,
)

# ... [Previous code for save_to_txt, get_all_topic, get_single_label remains the same] ...


def get_label_distribution(labels, all_category):
    distribution = {k: 0 for k in all_category}
    distribution["unknown"] = 0  # Add 'unknown' category
    for label in labels:
        if sum(label) == 0:
            distribution["unknown"] += 1
        else:
            for i, value in enumerate(label):
                if value == 1:
                    distribution[all_category[i]] += 1
    distribution = dict(sorted(distribution.items()))
    return distribution


def custom_multilabel_split(
    df, all_topics, test_size=0.2, dev_size=0.1, random_state=42, use_unknown=False
):
    random.seed(random_state)
    np.random.seed(random_state)

    # Convert labels to binary matrix
    label_matrix = np.array(df["label"].tolist())

    # Identify samples for each label
    label_indices = {
        label: set(np.where(label_matrix[:, i] == 1)[0])
        for i, label in enumerate(all_topics)
    }

    # Find samples with empty labels (unknown)
    unknown_indices = set(np.where(np.sum(label_matrix, axis=1) == 0)[0])

    if not use_unknown:
        # If use_unknown is False, remove samples with empty labels from consideration
        valid_indices = set(range(len(df))) - unknown_indices
        df = df.iloc[list(valid_indices)].reset_index(drop=True)
        # Recalculate label matrix and indices after filtering
        label_matrix = np.array(df["label"].tolist())
        label_indices = {
            label: set(np.where(label_matrix[:, i] == 1)[0])
            for i, label in enumerate(all_topics)
        }
        unknown_indices = set()  # Empty set since we're not using unknown labels

    # Calculate the number of samples for test and dev sets
    n_test = int(len(df) * test_size)
    n_dev = int(len(df) * dev_size)

    # Ensure at least one sample per label in test set
    test_indices = set()
    for label, indices in label_indices.items():
        if indices:
            test_indices.add(random.choice(list(indices)))

    if use_unknown and unknown_indices:
        # Add unknown samples to test set proportionally
        n_unknown_test = int(len(unknown_indices) * test_size)
        test_indices.update(set(random.sample(list(unknown_indices), n_unknown_test)))

    # Add more samples to test set if needed
    while len(test_indices) < n_test:
        remaining = set(range(len(df))) - test_indices
        if remaining:  # Check if there are remaining samples
            test_indices.add(random.choice(list(remaining)))

    # Select dev set from remaining samples
    remaining = list(set(range(len(df))) - test_indices)

    if use_unknown:
        # Handle unknown samples in dev set if use_unknown is True
        remaining_unknown = list(unknown_indices - test_indices)
        n_unknown_dev = int(len(remaining_unknown) * (dev_size / (1 - test_size)))
        if remaining_unknown:
            dev_indices = set(
                np.random.choice(
                    [i for i in remaining if i not in remaining_unknown],
                    size=min(
                        n_dev - n_unknown_dev, len(remaining) - len(remaining_unknown)
                    ),
                    replace=False,
                )
            )
            dev_indices.update(
                set(
                    random.sample(
                        remaining_unknown, min(n_unknown_dev, len(remaining_unknown))
                    )
                )
            )
        else:
            dev_indices = set(
                np.random.choice(
                    remaining, size=min(n_dev, len(remaining)), replace=False
                )
            )
    else:
        # Simple dev set selection when not using unknown labels
        dev_indices = set(
            np.random.choice(remaining, size=min(n_dev, len(remaining)), replace=False)
        )

    # Remaining samples go to train set
    all_indices = set(range(len(df)))
    if not use_unknown:
        # Remove unknown indices from consideration for train set
        all_indices = all_indices - unknown_indices
    train_indices = all_indices - test_indices - dev_indices

    # Create DataFrames
    train = df.iloc[list(train_indices)].reset_index(drop=True)
    dev = df.iloc[list(dev_indices)].reset_index(drop=True)
    test = df.iloc[list(test_indices)].reset_index(drop=True)

    return train, dev, test


MODE = "topic"
USE_UNKNOWN = False

# fname = "./xlsx/Climate Worksheet.xlsx"
fname = "/home/miftah/Downloads/giz/finetune_huggingface/xlsx/Climate Worksheet_5_nov_2024.xlsx"
df = pd.read_excel(fname, sheet_name=None)

sheets = ["topic"]
texts_a = []
labels = []
all_category = []

for sheet in sheets:
    di = df[sheet]
    # di = di.dropna(subset=["Title", "Topic", "Subtopic"])
    di = di.dropna(subset=["Title", "Topic"])
    di = di.drop_duplicates(subset="Title", keep="first")
    if MODE == "topic":
        all_category = get_all_multilabel_class(di, "Topic", mode=MODE)
    elif MODE == "subtopic":
        all_category = get_all_multilabel_class(di, "Subtopic", mode=MODE)
    all_category = remove_small_topic(all_category, mode=MODE)

    for i, row in di.iterrows():
        title = row["Title"]
        content = row["Content"]
        article = f"{title}. {content}"

        # topic = fix_set(row["Topic"], mode="topic")
        text_a = article
        single_label = "unassigned"
        if MODE == "topic":
            single_label = get_single_label(row["Topic"], all_category, mode=MODE)
        elif MODE == "subtopic":
            text_a = f"TOPIK ARTIKEL:\n{topic}\nTEKS BERITA:\n{article}"
            single_label = get_single_label(row["Subtopic"], all_category, mode=MODE)
        texts_a.append(text_a)
        labels.append(single_label)

df = pd.DataFrame({"text_a": texts_a, "label": labels})

# Perform custom split
train, dev, test = custom_multilabel_split(
    df,
    all_category,
    test_size=0.1,
    dev_size=0.1,
    random_state=42,
    use_unknown=USE_UNKNOWN,
)


def df_to_dict_pickle(df, outd, dtype):
    data_dict = {col: df[col].tolist() for col in df.columns}
    pickle_file_path = f"{outd}/{dtype}.pkl"
    with open(pickle_file_path, "wb") as f:
        pickle.dump(data_dict, f)
    print(f"Dictionary saved to {pickle_file_path}\n")
    return data_dict


# Create output directory
d = f"{MODE}_multilabel_v3"
outd = f"{d}/data"
os.makedirs(outd, exist_ok=True)

df_to_dict_pickle(train, outd, dtype="train")
df_to_dict_pickle(dev, outd, dtype="dev")
df_to_dict_pickle(test, outd, dtype="test")

print(f"\nData is split and saved in {outd}:\n")
print(f"Train set: {len(train)} samples\n")
print(f"Dev set: {len(dev)} samples\n")
print(f"Test set: {len(test)} samples\n")

all_data_distribution = get_label_distribution(df["label"], all_category)
print("\nAll data label distribution (before split):\n")
for topic, count in all_data_distribution.items():
    print(f"{topic}: {count}\n")

# Calculate and print label distribution for each set
for dataset, name in [(train, "Train"), (dev, "Dev"), (test, "Test")]:
    distribution = get_label_distribution(dataset["label"], all_category)
    print(f"\n{name} set label distribution:\n")
    for topic, count in distribution.items():
        print(f"{topic}: {count}\n")

# Save labels
unique_labels = "\n".join(all_category)
with open(f"{outd}/labels.txt", "w") as f:
    f.write(unique_labels)
print(f"\nUnique labels saved to {outd}/labels.txt")
