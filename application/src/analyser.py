
import difflib

from constants.text import *

def get_best_sequence(text, pattern, cutoff=0.85):
    pattern_length = len(pattern)
    store = []
    for i in range(len(text) - pattern_length + 1):
        substring = text[i : i + pattern_length]
        similarity = difflib.SequenceMatcher(None, substring, pattern).ratio()
        if similarity < 0.3:
            i = min(i+2, len(text) - pattern_length-1)
            continue
        if similarity == 1:
            return i
        if similarity >= cutoff:
            store.append((similarity, i))
    if len(store) == 0:
        return -1
    if len(store) == 1:
        return store[0][1]
    max_similarity, max_index = 0, 0
    for (similarity, index) in store:
        if similarity > max_similarity:
            max_similarity = similarity
            max_index = index
    return max_index

def has_sequence(text, pattern, cutoff=0.85):
    pattern_length = len(pattern)
    for i in range(len(text) - pattern_length + 1):
        substring = text[i : i + pattern_length]
        similarity = difflib.SequenceMatcher(None, substring, pattern).ratio()
        if similarity < 0.3:
            i = min(i+2, len(text) - pattern_length-1)
            continue
        if similarity >= cutoff:
            return True
    return False

def has_title(text, *keys):
    for key in keys:
        if has_sequence(text, key):
            print("TITLE IS", key)
            return True
    return False

def clean_string(string):
    for remove in REMOVE_AT_THE_END:
        string = string.replace(remove, "")
    string = string.replace("l", "I").upper()
    for old, new in REPLACE_AT_THE_END:
        string = string.replace(old, new)
    return string

def get_last_index_for_string(text, *keys):
    for key in keys:
        index = get_best_sequence(text, key)
        if index != -1:
            return index + len(key)
    return -1
