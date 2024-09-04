# from unittest import skip
# from rest_framework import status
# from rest_framework.reverse import reverse
# from core.tests import BaseAPITest


# @skip("Skip Sub county tests.")
# class SubCountyTests(BaseAPITest):
#     def create_sub_county(self, county="1", name="madC"):
#         data = {"county": county, "name": name}
#         return self.auth_client.post(reverse("list_create_sub_countys"), data=data)

#     def setUp(self):
#         super(SubCountyTests, self).setUp()
#         self.create_sub_county()

#     def test_creating_sub_county(self):
#         resp = self.create_sub_county(name="madC")
#         # print(resp.json())
#         self.assertEquals(resp.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_listing_sub_county(self):
#         resp = self.auth_client.get(reverse("list_create_sub_countys"))
#         # print(resp.json())
#         self.assertEquals(resp.status_code, status.HTTP_200_OK)

#     def test_retrieving_sub_county(self):
#         resp = self.auth_client.get(reverse("retrieve_update_destroy_sub_county", kwargs={"pk": 1}))
#         # print(resp.json())
#         self.assertEquals(resp.status_code, status.HTTP_200_OK)
#         self.assertEquals(resp.data["name"], "madC")

#     def test_updating_sub_county(self):
#         resp = self.auth_client.patch(reverse("retrieve_update_destroy_sub_county", kwargs={"pk": 1}), data={"name": "madC"})
#         self.assertEquals(resp.status_code, status.HTTP_200_OK)
#         self.assertEquals(resp.data["name"], "madC")
