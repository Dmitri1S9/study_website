import json
import math
from collections import Counter
import spacy
import re
from typing import Set, Tuple, List, Dict, Any

class TextDataProcessor:
    def __init__(self) -> None:
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.ignore_words = get_ignore_words()

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Removes URLs and non-alphabetic characters from text.
        """
        text = re.sub(r"http\S+|www\S+|https\S+", "", text)
        text = re.sub(r"[^A-Za-z\s']", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_words(self, text: str, pos_tag: str) -> List[str]:
        """
        Extracts lemmatized words of a given part of speech from text.
        """
        doc = self.nlp(text)

        return [
            token.lemma_.lower() for token in doc
            if token.pos_ == pos_tag
            and token.lemma_.lower() not in self.ignore_words
        ]

    def process_counters(self) -> Tuple[Counter, Counter]:
        """
        Processes the database and returns counters for adjectives and nouns.
        """
        with open("data/db.json", "r", encoding="utf-8") as file:
            database: Dict[str, Any] = json.load(file)

        adjective_counter: Counter = Counter()
        noun_counter: Counter = Counter()

        for user_name, user_posts in database.items():
            for post in user_posts:
                title_text: str = self.clean_text(post["title"])
                for adjective in self.extract_words(title_text, "ADJ"):
                    adjective_counter[adjective] += int(math.log(int(post["score"]) + 1))
                for noun in self.extract_words(title_text, "NOUN"):
                    noun_counter[noun] += int(math.log(int(post["score"]) + 1))

                for comment in post["comments"]:
                    comment_text: str = self.clean_text(comment["text"])
                    comment_adjectives: List[str] = self.extract_words(comment_text, "ADJ")
                    for adjective in comment_adjectives:
                        adjective_counter[adjective] += int(math.log(int(comment["score"]) + 1))

                    comment_nouns: List[str] = self.extract_words(comment_text, "NOUN")
                    for noun in comment_nouns:
                        noun_counter[noun] += int(math.log(int(comment["score"]) + 1))

        # For debugging: print most common adjectives with their synonyms
        for word, freq in adjective_counter.most_common():
            print(f"{word} {freq}")

        return adjective_counter, noun_counter

def get_ignore_words() -> Set[str]:
    """
    Loads and returns a set of words to ignore from a JSON file.
    """
    with open("data/ignore_words.json", "r", encoding="utf-8") as file:
        return set(word.strip().lower() for word in json.load(file))

if __name__ == "__main__":
    print(get_ignore_words())
    processor = TextDataProcessor()
    processor.process_counters()
