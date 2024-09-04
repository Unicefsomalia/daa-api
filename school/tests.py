from django.test import TestCase, tag

# Create your tests here.
from rest_framework import status
from rest_framework.reverse import reverse

from core.tests import BaseAPITest


class SchoolTests(BaseAPITest):
    def test_creating_school(self):
        resp = self.create_school(name="TeSchool", emis_code="3452")
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

    @tag("lsc")
    def test_list_searching_schools(self):
        url = "{}?name=sch".format(reverse("list_search_schools"))
        resp = self.auth_client.get(url)
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 2)

        url = "{}?name=sch2".format(reverse("list_search_schools"))
        resp = self.auth_client.get(url)
        self.assertEquals(resp.json()["count"], 1)
        # print(resp.json())

    def test_retrieving_school(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_school", kwargs={"pk": 1}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "TheSchool")

    def test_updating_school(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_school", kwargs={"pk": 1}), data={"name": "Hello"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "Hello")

    # def test_listing_school_districts(self):
    #     resp = self.auth_client.get(reverse("list_school_districts", kwargs={"pk": 1}))
    #     self.assertEquals(resp.data["count"],1)
    #     self.assertEquals(resp.status_code,200)
