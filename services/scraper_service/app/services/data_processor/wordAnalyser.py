from nltk.corpus import wordnet as wn

def get_related_words(word):
    related_words = set()

    for syn in wn.synsets(word):
        for lemma in syn.lemmas():
            related_words.add(_process_word(lemma.name()))
            for dr in lemma.derivationally_related_forms():
                related_words.add(_process_word(dr.name()))

    return related_words

def _process_word(word: str) -> str:
    word = word.replace('-', ' ')
    word = word.lower()
    return word


if __name__ == "__main__":
    ...
