from typing import List

from label_fix import (
    subtopic_phrase_fix,
    subtopic_word_fix,
    topic_phrase_fix,
    topic_word_fix,
)


def fix(input_topic):
    t = input_topic.lower()
    t = " ".join(t.split())
    for k, v in topic_word_fix.items():
        t = t.replace(k, v)
        if t in topic_phrase_fix:
            t = topic_phrase_fix[t]
    return t


def fix_subtopic(input_subtopic):
    t = input_subtopic.lower().strip()
    for k, v in subtopic_word_fix.items():
        t = t.replace(k, v)
        if t in subtopic_phrase_fix:
            t = subtopic_phrase_fix[t]
    return t


def fix_set(topics_str, mode="topic"):
    topics = []
    for topic in topics_str.split("\n"):
        t = topic
        if mode == "topic":
            t = fix(t)
        elif mode == "subtopic":
            t = fix_subtopic(t)
        topics.append(t)
    new_topic_str = "\n".join(topics)
    return new_topic_str


def save_to_txt(fname, text):
    with open(fname, "w+") as f:
        f.write(text)


def get_all_multilabel_class(df, col_name, mode="topic"):
    raw_topics = df[col_name].unique()
    topics = []
    for raw_topic in raw_topics:
        tmp = raw_topic.split("\n")
        for t in tmp:
            if mode == "topic":
                t = fix(t)
            elif mode == "subtopic":
                t = fix_subtopic(t)
            if t:
                if t not in topics:
                    topics.append(t)
    return sorted(topics)


def remove_small_topic(all_topics, mode="topic"):
    fname = "skip_topic_labels.txt"
    if mode == "subtopic":
        fname = "skip_subtopic_labels.txt"
    skip_labels = open(fname).read().splitlines()
    filtered_topics = [x for x in all_topics if x not in skip_labels]
    return filtered_topics


def get_single_label(topics_str: str, all_topics: List[str], mode="topic") -> dict:
    single_dic = {k: 0 for k in all_topics}
    for topic in topics_str.split("\n"):
        t = topic
        if mode == "topic":
            t = fix(t)
        elif mode == "subtopic":
            t = fix_subtopic(t)
        if not t:
            continue
        if t in single_dic:
            single_dic[t] = 1
        # else:
        #     print(f"ERROR. topic: {t} not found in collection of topics")
        #     exit()
    res = list(single_dic.values())
    return res
