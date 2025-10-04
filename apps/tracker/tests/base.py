from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class BaseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.status = status
        self.data = None
        self.updated_data = None

    def __repr__(self) -> str:
        raise NotImplementedError("Subclasses must implement __repr__ method")

    def _post(self):
        if self.data is None:
            raise ValueError("Data for POST request does not exist")
        return self.client.post(f'/api/{repr(self)}/', self.data, format='json')

    def _get(self):
        self._post()
        return self.client.get(f'/api/{repr(self)}/')

    def _update(self):
        obj_id = self._post().data['id']
        return self.client.put(f'/api/{repr(self)}/{obj_id}/', self.updated_data, format='json')

    def _delete(self):
        obj_id = self._post().data['id']
        return self.client.delete(f'/api/{repr(self)}/{obj_id}/')

