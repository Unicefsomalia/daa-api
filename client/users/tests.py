from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from client.models import MyUser
from mylib.my_common import MyUserRoles
from core.tests import BaseAPITest


class SystemUsersCountyTests(BaseAPITest):
    admin_id = None

    def setUp(self):
        super(SystemUsersCountyTests, self).setUp()
        # self.create_county()
        self.admin_id = self.create_super_user_my()

    def create_super_user_my(self):
        return MyUser.objects.create_superuser("madmin112", "madmin1112@gmail.com", "m")

    def create_user(
        self,
        role=MyUserRoles.SCHT.name,
        username="mad",
        ids=[1, 2],
    ):
        user = {"first_name": "Test", "last_name": "Doe", "username": username, "ids": ids, "password": "m", "role": role}
        cl = APIClient()
        cl.force_authenticate(user=self.admin_id)
        return cl.post(reverse("list_create_system_users"), user)

    @tag("cul")
    def test_listing_system_users(self):
        # self.set_authenticated_user(2)
        resp = self.auth_client.get(reverse("list_create_clients"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("cu")
    def test_creating_systemc_user(self):
        resp = self.create_user(
            role=MyUserRoles.SCHA.name,
            ids=["1"],
        )
        print(resp.json())
        self.assertEqual(resp.status_code, 201)

        resp = self.create_user(role=MyUserRoles.SCHT.name, username="ad")
        # print(resp.json())
        self.assertEqual(resp.status_code, 201)

        resp = self.create_user(role=MyUserRoles.DSTA.name, username="sub_county")
        # print(resp.json())
        self.assertEqual(resp.status_code, 201)

        resp = self.create_user(role=MyUserRoles.RGNA.name, username="county")
        self.assertEqual(resp.status_code, 201)
