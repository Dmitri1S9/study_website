import logging

from app.db import DBGet
from app.ml_client.ml_prediction import MLPrediction
from app.tasks import analyse_character_task
log = logging.getLogger(__name__)

class MLClient:
    def __init__(self):
        self.db_get = DBGet()
        self.predictor = MLPrediction()

    def get_feature_by_name(self, name: str):
        raise NotImplementedError

    def get_feature_by_name_and_universe(self, name: str, universe: str):
        try:
            character_id: int = int(self.db_get.get_character_id(name, universe)["id"])
            print(character_id)
        except TypeError:
            res = analyse_character_task.delay(name, universe)
            log.info(f"⏰⏰⏰⏰⏰ CHA IN QUEUE: {name}, {universe}, id_in_queue={res.id}")




if __name__ == "__main__":
    client = MLClient()
    client.get_feature_by_name_and_universe("Dart Maul", universe="Star Wars")
