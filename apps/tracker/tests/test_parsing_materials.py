from rest_framework.test import APIClient
from ..models import Title, Character
from .general_tests import GenericAPITest


class ParsingMaterialAPITest(GenericAPITest):
    def setUp(self):
        self.client = APIClient()
        self.title = Title.objects.create(name="test_title")
        self.character = Character.objects.create(
            name="test_character", title=self.title, description="Main protagonist"
        )
        self.data = {
            "character_id": self.character.id,
            "link": "https://github.com/Dmitri1S9/study_website"
        }
        self.updated_data = self.data.copy()
        self.updated_data["link"] = "https://open.spotify.com"

    def __repr__(self):
        return "parsing_materials"

