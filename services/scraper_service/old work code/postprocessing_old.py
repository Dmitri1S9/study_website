# import json
#
# import nltk
# from typing import Any, Dict, List, Set, Optional
# from nltk.corpus import wordnet
#
#
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
#
#
# class PostProcessing:
#     def __init__(self) -> None:
#         self.lexical_analyser = LexicalAnalyser()
#         # !!!!!!! It's just for testing purpose !!!!!!!
#         with open("../../test_data", "r") as f:
#             data = f.read().splitlines()
#         self._dirty_data = dict()
#         for line in data:
#             key, value = line.split()
#             self._dirty_data[key] = int(value)
#         # !!!!!!! It's just for testing purpose !!!!!!!
#
#         self.bias = int(max(self._dirty_data.values()) * 0.01) + 3
#         self._adj_res = self._get_words("adjectives")
#         self._adjectives = self._adj_res.values()
#         # self._noun_data = dict()
#
#
#     def _clear_rubbish(self) -> None:
#         """
#         delete 5% of words to avoid noise
#         """
#
#         for word in list(self._dirty_data.keys()):
#             if self._dirty_data[word] <= self.bias:
#                 del self._dirty_data[word]
#
#     @staticmethod
#     def _get_words(word_type:str) -> Dict[str, int]:
#         """
#         get adjectives/nouns from json file
#         """
#         if word_type not in ["adjectives", "nouns"]:
#             raise ValueError("Type must be 'adjectives' or 'nouns'")
#         with open(f"data/{word_type}.json", "r") as f:
#             return json.load(f)
#
#     def _get_characteristics(self) -> None:
#         """
#         get characteristics from adjectives and nouns(not implemented yet)
#         create clear image of character
#         """
#         for word in self._dirty_data:
#             if word in self._adjectives:
#                 self._adj_res[word] += self._dirty_data[word]
#             synonyms = self.lexical_analyser.get_synonyms(word)
#             antonyms = self.lexical_analyser.get_antonyms(word)
#             self._add_to_data(words=word, coefficient=0.7, synonyms=synonyms, antonyms=antonyms)
#             if self._dirty_data[word] >= (self.bias - 3) * 60 + 10:
#                 self._add_to_data(words=synonyms, coefficient=0.1, synonyms=synonyms, antonyms=antonyms)
#
#
#     def _add_to_data(self,
#                      words: List[str]|str,
#                      coefficient: float,
#                      synonyms:List[str],
#                      antonyms:List[str]
#                      ) -> None:
#         if isinstance(words, str):
#             words = [words]
#         for word in words:
#             for syn in synonyms:
#                 if syn in self._adj_res:
#                     self._adj_res[syn] += int(self._dirty_data[word] * coefficient)
#             for ant in antonyms:
#                 if ant in self._adj_res:
#                     self._adj_res[ant] -= int(self._dirty_data[word] * coefficient)
#
#
#
#     def _normalize(self) -> None:
#         """
#         normalize characteristics
#         """
#         raise NotImplementedError("This method is not implemented yet.")
#
#     def get_results(self) -> Dict[str, Any]:
#         """
#         get final results
#         """
#         try:
#             # self._clear_rubbish()
#             self._get_characteristics()
#             # self._normalize()
#             return self._adj_res
#         except NotImplementedError:
#             return {
#                 "status": "error",
#                 "message": "This method is not implemented yet."
#             }
#
# if __name__ == "__main__":
#     pp = PostProcessing()
#     print(pp.get_results())  # Example usage