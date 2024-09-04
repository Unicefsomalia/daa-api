from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from django.test import tag


class LocaleTranslationTextTests(BaseAPITest):
    def create_locale_translation_text(self, locale="1", text="1", translated_text="1"):
        data = {"locale": locale, "text": text, "translated_text": translated_text}
        return self.auth_client.post(reverse("list_create_locale_translation_texts"), data=data)

    def setUp(self):
        super(LocaleTranslationTextTests, self).setUp()
        resp = self.create_translation_locale()
        resp = self.create_translation_text()
        self.create_locale_translation_text()

    def test_creating_locale_translation_text(self):
        resp = self.create_locale_translation_text(translated_text="1")
        # print(resp.json())
        # self.assertEquals(resp.status_code, )

    def test_listing_locale_translation_text(self):
        resp = self.auth_client.get(reverse("list_create_locale_translation_texts"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("tll")
    def test_listing_locale_dynamic_stats_locale(self):
        url = reverse("list_dynamic_locale_translation_texts_statistics", kwargs={"type": "id"})
        resp = self.auth_client.get(url)
        # print(resp.json())

        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["count"], 1)

    @tag("tdl")
    def test_listing_locale_dynamic_stats(self):
        url = reverse("list_dynamic_locale_translation_texts_statistics", kwargs={"type": "id"})
        resp = self.auth_client.get(url)
        # print(resp.json())
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["count"], 1)
        resp = self.auth_client.get(f"{url}?original=za")
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 0)

        resp = self.auth_client.get(f"{url}?original=zaawaw")
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 0)

        resp = self.auth_client.get(f"{url}?not_translated=true")
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 1)

        resp = self.auth_client.get(f"{url}?not_translated=false")
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 0)

    def test_retrieving_locale_translation_text(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_locale_translation_text", kwargs={"pk": 1}))
        print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["translated_text"], None)

    def test_updating_locale_translation_text(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_locale_translation_text", kwargs={"pk": 1}), data={"translated_text": "1"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["translated_text"], "1")
