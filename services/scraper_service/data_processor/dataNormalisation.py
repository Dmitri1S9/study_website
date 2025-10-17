import json
from typing import Any, Dict, List, Set, Optional
from dataProcessor import DataProcessor

class DataPostProcessing(DataProcessor):
    @staticmethod
    def _normalize(self) -> None:
        """
        normalize characteristics
        """
        raise NotImplementedError("This method is not implemented yet.")

    def run(self):
        """
        get final results
        """
        self._create_result_database()
        self._process_text()
        self._collect_dirty_data()
        print(self)


if __name__ == "__main__":
    pp = DataPostProcessing()
    print(pp.run())  # Example usage