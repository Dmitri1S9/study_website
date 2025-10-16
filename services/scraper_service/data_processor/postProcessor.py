import json
from typing import Any, Dict, List, Set, Optional

class PostProcessing:
    def __init__(self) -> None:
        ...

    def _clear_rubbish(self) -> None:
        """
        delete 5% of words to avoid noise
        """

    @staticmethod
    def _get_words(word_type:str) -> Dict[str, int]:
        ...

    def _get_characteristics(self) -> None:
        ...


    def _normalize(self) -> None:
        """
        normalize characteristics
        """
        raise NotImplementedError("This method is not implemented yet.")

    def get_results(self) -> Dict[str, Any]:
        """
        get final results
        """
        try:
            ...
        except NotImplementedError:
            return {
                "status": "error",
                "message": "This method is not implemented yet."
            }

if __name__ == "__main__":
    pp = PostProcessing()
    print(pp.get_results())  # Example usage