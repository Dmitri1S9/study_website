import re
from typing import Set, List


class TextCleaner:
    @staticmethod
    def clean_text(text, ignore_words: Set[str]) -> List[str]:
        text = re.sub(r"http\S+|www\S+|https\S+", "", text)
        text = text.replace('-', ' ')
        text = text.lower()
        text = re.sub(r"[^A-Za-z\s']", " ", text)
        text = re.sub(r"\s+", " ", text)
        return [w for w in text.split() if w not in ignore_words]


