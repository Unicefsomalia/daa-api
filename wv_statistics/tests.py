from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.reverse import reverse

from core.tests import BaseAPITest


class SchoolTests(BaseAPITest):
    def test_listing_all_statistics(self):
        url = reverse("list_all_statistics")
        resp = self.auth_client.get(url)
        self.assertEquals(resp.status_code, 200)

        resp = self.auth_client.get("{}?school=1".format(url))
        self.assertEquals(resp.status_code, 200)
        # print(resp.json())

    def test_ping(self):
        resp = self.client.get(reverse("ping_server"))
        self.assertEquals(resp.status_code, 200)
        # print(resp.json())
