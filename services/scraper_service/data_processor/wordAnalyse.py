# class LexicalAnalyser:
#     @staticmethod
#     def get_synonyms(adjective: str) -> List[str]:
#         """
#         Returns a list of synonyms for the given adjective.
#         """
#         synonyms: Set[str] = set()
#         for synset in wordnet.synsets(adjective, pos=wordnet.ADJ):
#             for lemma in synset.lemmas():
#                 synonyms.add(lemma.name())
#         return list(synonyms)
#
#     @staticmethod
#     def get_antonyms(adjective: str) -> List[str]:
#         """
#         Returns a list of antonyms for the given adjective.
#         """
#         antonyms: Set[str] = set()
#         for synset in wordnet.synsets(adjective, pos=wordnet.ADJ):
#             for lemma in synset.lemmas():
#                 if lemma.antonyms():
#                     for ant in lemma.antonyms():
#                         antonyms.add(ant.name())
#         return list(antonyms)
#
#     def __init__(self) -> None:
#         nltk.download('wordnet')
#         nltk.download('omw-1.4')


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
