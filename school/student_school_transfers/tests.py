from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse
from client.models import MyUser
from core.tests import BaseAPITest
from school.models import Stream


class StudentSchoolTransferTests(BaseAPITest):
    def create_student_school_transfer(self, from_school="1", accept_class="1", reason="madC", student="1", to_school="1", accepted="1", complete="1"):
        data = {"from_school": from_school, "student": student, "accept_class": accept_class, "reason": reason, "to_school": to_school, "accepted": accepted, "complete": complete}
        return self.auth_client.post(reverse("list_create_student_school_transfers"), data=data)

    def setUp(self):
        super(StudentSchoolTransferTests, self).setUp()
        resp = self.create_student_school_transfer()
        # print(resp.json())

    @tag("cst")
    def test_creating_student_school_transfer(self):
        resp = self.create_student_school_transfer(reason="madC")
        print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

    @tag("lst")
    def test_listing_student_school_transfer(self):
        school_emis_code = Stream.objects.get(id=1).school.emis_code
        user = MyUser.objects.get(username=school_emis_code)
        self.set_authenticated_user(user.id)
        # print(user)
        resp = self.auth_client.get(reverse("list_create_student_school_transfers"))
        print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_student_school_transfer(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_student_school_transfer", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["reason"], "madC")

    def test_updating_student_school_transfer(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_student_school_transfer", kwargs={"pk": 1}), data={"reason": "madC"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["reason"], "madC")

    @tag("at")
    def test_accepting_student_school_transfer(self):
        resp = self.create_stream(base_class="1", name="ada")
        # print(resp.json())
        resp = self.auth_client.patch(reverse("accept_deny_student_school_transfer", kwargs={"pk": 1, "school_choice": "accept"}), data={})
        # print(resp.json())
        self.assertEquals(resp.status_code, 400)
        url = reverse("accept_deny_student_school_transfer", kwargs={"pk": 1, "school_choice": "accept"})
        # print(url)
        resp = self.auth_client.patch(url, data={"accept_stream": 4})
        # print(resp.json())
        # print(resp.json()["active"])
        # print(resp.json()["stream"], 2)
        self.assertEquals(resp.json()["stream"], 4)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.patch(reverse("retrieve_update_destroy_student_school_transfer", kwargs={"pk": 1}), data={"reason": "madC"})
        print(resp.json())
        self.assertEquals(resp.data["accepted"], True)
        self.assertEquals(resp.json()["complete"], True)

    @tag("atd")
    def test_denying_student_school_transfer(self):
        resp = self.auth_client.patch(reverse("accept_deny_student_school_transfer", kwargs={"pk": 1, "school_choice": "deny"}), data={"reason": "madC"})
        # print(resp.json())

        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.patch(reverse("retrieve_update_destroy_student_school_transfer", kwargs={"pk": 1}), data={"reason": "madC"})
        # print(resp.json())
        self.assertEquals(resp.data["accepted"], False)
