from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from django.test import tag


class TranslationTextTests(BaseAPITest):
    def setUp(self):
        super(TranslationTextTests, self).setUp()
        resp = self.create_translation_locale()
        resp = self.create_translation_text()

    def test_creating_translation_text(self):
        resp = self.create_translation_text(title="madC")
        # print(resp.json())
        self.assertEquals(resp.status_code, 400)

    def test_listing_translation_text(self):
        resp = self.auth_client.get(reverse("list_create_translation_texts"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_translation_text(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_translation_text", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["title"], "madC")

    def test_updating_translation_text(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_translation_text", kwargs={"pk": 1}), data={"title": "madC"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["title"], "madC")
