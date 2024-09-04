from pydoc import describe
from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest


class StudentIntergrateTests(BaseAPITest):
    def create_student_intergrate(self, student="1", description="1", from_stream="1", to_stream="2", completed="1"):
        data = {"student": student, "from_stream": from_stream, "description": description, "to_stream": to_stream, "completed": completed}
        return self.auth_client.post(reverse("list_create_student_intergrates"), data=data)

    def setUp(self):
        super(StudentIntergrateTests, self).setUp()
        self.create_student_intergrate()

    def test_creating_student_intergrate(self):
        resp = self.create_student_intergrate(description="1")
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

    def test_listing_student_intergrate(self):
        resp = self.auth_client.get(reverse("list_create_student_intergrates"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_student_intergrate(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_student_intergrate", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["description"], "1")

    def test_updating_student_intergrate(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_student_intergrate", kwargs={"pk": 1}), data={"description": "1"})
        self.assertEquals(resp.status_code, 405)
        # self.assertEquals(resp.data["description"], "1")

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_student_intergrate", kwargs={"pk": 1}))
        self.assertEquals(resp.status_code, 204)

    @tag("tsi")
    def test_intergration_flow(self):
        student_id = 2
        resp = self.auth_client.get(reverse("retrieve_update_destroy_student", kwargs={"pk": student_id}))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["stream"], 1)
        stream_id = resp.json()["stream"]
        to_stream_id = 2
        resp = self.create_student_intergrate(student=student_id, from_stream=stream_id, to_stream=to_stream_id)
        intergrate_id = resp.json()["id"]
        print(resp.json())

        resp = self.auth_client.get(reverse("retrieve_update_destroy_student", kwargs={"pk": student_id}))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["stream"], to_stream_id)

        # Trigget another intergration
        to_to_stream_id = 3
        resp = self.create_student_intergrate(student=student_id, from_stream=to_stream_id, to_stream=to_to_stream_id)
        # intergrate_id = resp.json()["id"]

        resp = self.auth_client.get(reverse("retrieve_update_destroy_student", kwargs={"pk": student_id}))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["stream"], to_to_stream_id)

        resp = self.auth_client.delete(reverse("retrieve_update_destroy_student_intergrate", kwargs={"pk": intergrate_id}))
        self.assertEquals(resp.status_code, 204)

        resp = self.auth_client.get(reverse("retrieve_update_destroy_student", kwargs={"pk": student_id}))
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["stream"], to_to_stream_id)
