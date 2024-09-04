from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest


class VillageTests(BaseAPITest):
    def setUp(self):
        super(VillageTests, self).setUp()
        self.create_village()

    def test_creating_village(self):
        resp = self.create_village(name="madC1")
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

    def test_listing_village(self):
        resp = self.auth_client.get(reverse("list_create_villages"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_village(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_village", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC")

    def test_updating_village(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_village", kwargs={"pk": 1}), data={"name": "madC"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC")
