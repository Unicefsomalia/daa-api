from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from django.test import tag


class NoAttendanceHistoryTests(BaseAPITest):
    def create_no_attendance_history(self, start_date="2023-01-13", end_date="2023-02-13"):
        data = {"start_date": start_date, "end_date": end_date}
        return self.auth_client.post(reverse("list_create_no_attendance_historys"), data=data)

    def setUp(self):
        super(NoAttendanceHistoryTests, self).setUp()

    @tag("cnat")
    def test_creating_no_attendance_history(self):
        self.take_attendance(date="2023-02-13")
        resp = self.create_no_attendance_history(start_date="2023-02-12")
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

    def test_listing_no_attendance_history(self):
        resp = self.auth_client.get(reverse("list_create_no_attendance_historys"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_no_attendance_history(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_no_attendance_history", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, 404)
        # self.assertEquals(resp.data["id"], "madC")

    def test_updating_no_attendance_history(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_no_attendance_history", kwargs={"pk": 1}), data={"id": "madC"})
        self.assertEquals(resp.status_code, 404)

    @tag("natt")
    def test_no_attendance_stats(self):
        self.create_absent_reason(name="error")
        self.create_no_attendance_history()
        self.create_no_attendance_history()

        resp = self.create_absent_reason(name="other")
        # print(resp.json())
        resp = self.create_student_absent_reason(reason=1, description="TeStudentAbsentReason1", student=1, date="2019-09-09")

        self.assertEquals(resp.status_code, 201)

        url = reverse("list_dynamic_student_no_attendance_statistics", kwargs={"type": "id"})
        resp = self.auth_client.get(url)
        # print(resp.json())
        self.assertEquals(resp.status_code, 200)

        url = reverse("list_dynamic_student_no_attendance_statistics", kwargs={"type": "stream"})
        resp = self.auth_client.get(url)
        # print(resp.json())
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json()["count"], 3)
        self.assertEquals(resp.json()["results"][0]["total_missed_attendances"], 32)

        # url = reverse("list_dynamic_student_no_attendance_statistics", kwargs={"type": "id"})
        # resp = self.auth_client.get(url)
        # # print(resp.json())
        # print(resp.json()["results"][0])
        # self.assertEquals(resp.status_code, 200)

        # url = reverse("list_dynamic_student_no_attendance_statistics", kwargs={"type": "reason"})
        # resp = self.auth_client.get(url)
        # # print(resp.json()["results"][0])
        # # print(resp.json())
        # self.assertEquals(resp.status_code, 200)
        # self.assertEquals(resp.json()["count"], 3)

        # url = reverse("list_dynamic_student_no_attendance_statistics", kwargs={"type": "reason-description"})
        # resp = self.auth_client.get(url)
        # print(resp.json()["results"][0])
        # # print(resp.json())
        # self.assertEquals(resp.status_code, 200)
        # self.assertEquals(resp.json()["count"], 3)
