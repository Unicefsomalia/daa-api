from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from django.test import tag


class StateTests(BaseAPITest):
    def setUp(self):
        super(StateTests, self).setUp()
        self.create_state()

    def test_creating_state(self):
        resp = self.create_state(name="madC")
        # print(resp.json())
        self.assertEquals(resp.status_code, 400)

    def test_listing_state(self):
        resp = self.auth_client.get(reverse("list_create_states"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_state(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_state", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC")

    def test_updating_state(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_state", kwargs={"pk": 1}), data={"name": "madC"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC")
