from .general_tests import GenericAPITest
from rest_framework.test import APIClient

class TitleAPITest(GenericAPITest):
    def setUp(self):
        self.client = APIClient()
        self.data = {"name": "test_title"}
        self.updated_data = {"name": "new name"}

    def __repr__(self):
        return "titles"

    def test_get(self):
        super().test_get()
        self.assertEqual(self.response.data[0]["name"], "test_title")

    def test_update(self):
        super().test_update()
        self.assertEqual(self.response.data["name"], "new name")