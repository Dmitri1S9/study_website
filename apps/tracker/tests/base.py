from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class BaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.status = status
        self.data = None

    def __repr__(self) -> str:
        raise NotImplementedError("Subclasses must implement __repr__ method")

    def _post(self):
        if self.data is None:
            raise ValueError("Data for POST request does not exist")
        return self.client.post(f'/api/{repr(self)}/', self.data, format='json')

    def _get(self):
        self._post()
        return self.client.get(f'/api/{repr(self)}/')



