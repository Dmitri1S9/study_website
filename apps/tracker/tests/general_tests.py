from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.tracker.tests.base import BaseAPITest


class GenericAPITest(BaseAPITest):
    def test_post(self):
        if type(self) is GenericAPITest:
            return

        response = self._post()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get(self):
        if type(self) is GenericAPITest:
            return

        self.response = self._get()
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.response.data), 1)
