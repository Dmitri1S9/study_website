from .general_tests import GenericAPITest
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Title

class TitleAPITest(GenericAPITest):
    def setUp(self):
        self.client = APIClient()
        self.data = {"name": "test_title"}

    def __repr__(self):
        return "titles"

    def test_get(self):
        super().test_get()
        self.assertEqual(self.response.data[0]["name"], "test_title")