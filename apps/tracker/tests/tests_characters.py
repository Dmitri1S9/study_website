from rest_framework.test import APIClient
from rest_framework import status
from ..models import Title, Character
from .general_tests import GenericAPITest


class CharacterAPITest(GenericAPITest):
    def setUp(self):
        self.client = APIClient()
        self.title = Title.objects.create(name="Attack on Titan")
        self.data = {
            "name": "Levi",
            "title_id": self.title.id,
            "description": "Strongest soldier"
        }

    def __repr__(self):
        return "characters"

    def test_post(self):
        super()._post()
        self.assertEqual(Character.objects.get().name, self.data["name"])

    def test_get(self):
        super().test_get()
        character = self.response.data[0]
        self.assertEqual(character['name'], self.data['name'])
        self.assertEqual(character['description'], self.data['description'])
        self.assertEqual(character['title']['id'], self.data['title_id'])