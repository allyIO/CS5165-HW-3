import os
import re
import socket
from collections import Counter

DATA_DIR = "/home/data"
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "result.txt")

IF_FILE = os.path.join(DATA_DIR, "IF.txt")
ARUTW_FILE = os.path.join(DATA_DIR, "AlwaysRememberUsThisWay.txt")

# A "word" = letters/digits, optionally with internal apostrophes (so "can't" is one token)
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*")


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def tokenize(text):
    """Lowercased words; contractions stay as a single token."""
    return [w.lower() for w in WORD_RE.findall(text)]


# Irregular contractions that can't be handled by a suffix rule
IRREGULAR_CONTRACTIONS = {
    "can't": ["can", "not"],
    "won't": ["will", "not"],
    "shan't": ["shall", "not"],
    "ain't": ["is", "not"],
    "let's": ["let", "us"],
    "y'all": ["you", "all"],
}

# Suffix contractions: (suffix, expansion)
SUFFIX_CONTRACTIONS = [
    ("n't", "not"),    # don't -> do not, isn't -> is not
    ("'m", "am"),      # I'm -> I am
    ("'re", "are"),    # you're -> you are
    ("'ve", "have"),   # I've -> I have
    ("'ll", "will"),   # we'll -> we will
    ("'d", "would"),   # I'd -> I would
]

# Words where 's means "is" (otherwise it's treated as possessive and dropped)
IS_CONTRACTION_BASES = {
    "it", "that", "there", "here", "what", "who", "where", "how",
    "he", "she", "when", "why", "this",
}


def expand_contraction(token):
    """Expand one lowercased token into a list of words."""
    token = token.replace("’", "'")
    if "'" not in token:
        return [token]

    if token in IRREGULAR_CONTRACTIONS:
        return list(IRREGULAR_CONTRACTIONS[token])

    for suffix, expansion in SUFFIX_CONTRACTIONS:
        if token.endswith(suffix):
            base = token[: -len(suffix)]
            if base:
                return [base, expansion]

    if token.endswith("'s"):
        base = token[:-2]
        if base in IS_CONTRACTION_BASES:
            return [base, "is"]
        return [base]  # possessive (e.g. "John's" -> "john")

    # Unknown pattern: fall back to splitting on the apostrophe
    return [p for p in token.split("'") if p]


def tokenize_split_contractions(text):
    """Lowercased words; contractions are expanded into their full words
    (I'm -> i, am | can't -> can, not | don't -> do, not)."""
    words = []
    for token in tokenize(text):
        words.extend(expand_contraction(token))
    return words


def get_ip_address():
    ip_address = socket.gethostbyname(socket.gethostname())
    return ip_address


def main():
    if_text = read_text(IF_FILE)
    arutw_text = read_text(ARUTW_FILE)

    # 1a / 1b: word counts
    if_count = len(tokenize(if_text))
    arutw_count = len(tokenize(arutw_text))
    grand_total = if_count + arutw_count

    # 1c: top 3 in IF.txt
    if_top3 = Counter(tokenize(if_text)).most_common(3)

    # 1d: top 3 in AlwaysRememberUsThisWay.txt with contractions split
    arutw_top3 = Counter(tokenize_split_contractions(arutw_text)).most_common(3)

    # 1e: IP address
    ip = get_ip_address()

    lines = [
        f"Word count in IF.txt: {if_count}",
        f"Word count in AlwaysRememberUsThisWay.txt: {arutw_count}",
        f"Grand total word count: {grand_total}",
        "",
        "Top 3 words in IF.txt:",
        *[f"  {i}. {w} - {c}" for i, (w, c) in enumerate(if_top3, 1)],
        "",
        "Top 3 words in AlwaysRememberUsThisWay.txt (contractions expanded):",
        *[f"  {i}. {w} - {c}" for i, (w, c) in enumerate(arutw_top3, 1)],
        "",
        f"IP address: {ip}",
    ]
    output = "\n".join(lines) + "\n"

    # 1f: write results, then print them
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()