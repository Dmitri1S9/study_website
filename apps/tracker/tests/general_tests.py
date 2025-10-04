from rest_framework import status
from apps.tracker.tests.base import BaseAPITest


class GenericAPITest(BaseAPITest):
    def generic_test(self, func: callable, status_code):
        if type(self) is GenericAPITest:
            return
        self.response = func()
        self.assertEqual(self.response.status_code, status_code)
        if func == self._get:
            self.assertEqual(len(self.response.data), 1)


    def test_post(self):
        self.generic_test(self._post, status.HTTP_201_CREATED)

    def test_get(self):
        self.generic_test(self._get, status.HTTP_200_OK)

    def test_update(self):
        self.generic_test(self._update, status.HTTP_200_OK)

    def test_delete(self):
        self.generic_test(self._delete, status.HTTP_204_NO_CONTENT)