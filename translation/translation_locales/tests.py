from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from django.test import tag

from translation.models import LocaleTranslationText


class TranslationLocaleTests(BaseAPITest):
    def setUp(self):
        super(TranslationLocaleTests, self).setUp()
        self.create_translation_locale()

    def test_creating_translation_locale(self):
        resp = self.create_translation_locale(name="Somali")
        # print(resp.json())
        self.assertEquals(resp.status_code, 400)

    @tag("ltl")
    def test_listing_translation_locale(self):
        resp = self.auth_client.get(reverse("list_create_translation_locales"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("lftl")
    def test_listing_flutter_formatted_translation_locale(self):
        LocaleTranslationText.objects.filter(id=1).update(translated_text="haahdar")
        resp = self.auth_client.get(reverse("list_flutter_formatted_translation_locales"))
        # print(resp.json())

    def test_retrieving_translation_locale(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_translation_locale", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "Somali")

    def test_updating_translation_locale(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_translation_locale", kwargs={"pk": 1}), data={"name": "Somalia"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "Somalia")
