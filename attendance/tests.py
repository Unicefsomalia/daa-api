from django.test import TestCase, tag
from attendance.models import AttendanceHistory

# Create your tests here.
from rest_framework import status
from rest_framework.reverse import reverse

from attendance.models import Attendance, TeacherAttendance
from core.tests import BaseAPITest
from school.models import Student


class AttendanceTests(BaseAPITest):
    #

    def test_fetching_attendances(self):
        resp = self.auth_client.get(reverse("list_create_attendances"))
        self.assertEquals(resp.status_code, 200)
        # print(resp.json())

    @tag("takeAtt")
    def test_creating_attendance(self):
        resp = self.take_attendance(date="2019-09-05", present=[1, 2], absent=[])
        resp = self.take_attendance(date="2019-09-06")
        # print(resp.json())
        count = AttendanceHistory.objects.all().count()
        # print(f"Attendacnes {count}")
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        self.assertEquals(count, 3)

    @tag("tce")
    # @skipIf("--tag=tce" not in sys.argv, "Skipping ")
    def test_creating_custom_export(self):
        self.create_student(first_name="MMhad",stream=2)
        self.school_2_take_attendance()
        # resp = self.create_custom_export(custom_report_name="overall",start_date="2025-01-01",end_date="2025-01-01")
        resp = self.create_custom_export(custom_report_name="overall",)
        # print(resp.json())
         
        self.assertEquals(resp.status_code, 201)
        id = resp.json()["id"]
        resp = self.auth_client.get(reverse("retrieve_update_destroy_export", kwargs={"pk": id}))
        # print(resp.json())
        
    @tag("takeT")
    def test_creating_teacher_attendance(self):
        resp = self.take_attendance(date="2019-09-05", present=[1], absent=[], stream="teachers")
        self.assertEquals(resp.status_code, 201)
        attendance = TeacherAttendance.objects.values("teacher_id", "status")
        self.assertEquals(len(attendance), 1)
        self.assertEquals(attendance[0]["status"], 1)

        resp = self.take_attendance(date="2019-09-05", present=[], absent=[1], stream="teachers")
        print(resp.json())
        self.assertEquals(resp.status_code, 201)
        attendance = TeacherAttendance.objects.values("teacher_id", "status")
        self.assertEquals(len(attendance), 1)
        self.assertEquals(attendance[0]["status"], 0)

    def test_retrieving_attendance(self):
        resp = self.client.get(reverse("retrieve_update_destroy_attendance", kwargs={"pk": "201909091"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["id"], "201909091")

    def test_updating_attendance(self):
        resp = self.client.patch(reverse("retrieve_update_destroy_attendance", kwargs={"pk": "201909091"}), data={"date": "2019-07-01T12:0:00"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["date"], "2019-07-01T12:00:00+03:00")

    @tag("dsi")
    def test_dynamic_id_response(self):
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "student"})
        resp = self.auth_client.get(url)
        print(resp.json())

    @tag("atsp")
    def test_listing_statistics_filter_special_needs(self):
        resp = self.create_special_need(name="MadCoew")
        id = resp.json()["id"]
        self.take_attendance(date="2019-09-06")
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "special-need"})
        resp = self.auth_client.get(url)
        self.assertEquals(resp.json()["count"], 1)

        # print(resp.json())
        resp = self.auth_client.get(f"{url}?special_needs={id}")
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 0)

        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "special-need"})
        resp = self.auth_client.get(f"{url}?special_needs=1")
        self.assertEquals(resp.json()["count"], 1)

    @tag("ldt")
    def test_listing_dynamic_test(self):
        # special_needs

        self.take_attendance(date="2023-02-9", present=[], absent=[1, 2])
        self.take_attendance(date="2023-02-10", present=[1], absent=[2])
        self.take_attendance(date="2023-02-11", present=[1], absent=[2])
        self.take_attendance(date="2023-02-12", present=[], absent=[1, 2])
        self.take_attendance(date="2023-02-13", present=[1], absent=[2])
        self.take_attendance(date="2023-02-14", present=[1, 2], absent=[])
        st = Student.objects.get(id=2)
        st.special_needs.set([])
        st.save()
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "special-need"})
        resp = self.auth_client.get(f"{url}?export=false")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        # print(resp.json())

        # return
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "special-need"})
        resp = self.auth_client.get(f"{url}?export=false")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.get(reverse("list_dynamic_attendances_statistics", kwargs={"type": "day"}))
        # print(resp.json()["count"])
        days_count = resp.json()["count"]
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.get(reverse("list_dynamic_attendances_statistics", kwargs={"type": "week"}))
        # print(resp.json())
        # days_count = resp.json()["count"]
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.get(reverse("list_dynamic_attendances_statistics", kwargs={"type": "class"}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.get(reverse("list_dynamic_attendances_statistics", kwargs={"type": "stream"}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.json()["results"][0]["total_days"], days_count)

    def test_listing_statistics(self):
        self.take_attendance(date="2019-09-06")
        self.take_attendance(date="2019-09-07")
        #
        self.create_school(name="school_2", emis_code="45")
        resp = self.create_stream(base_class="3", school=2)
        stream_id = resp.data["id"]
        resp = self.create_student(
            first_name="micha",
            stream=stream_id,
        )
        student_id = resp.data[0]["id"]
        resp = self.take_attendance_for_student(student=student_id, stream=stream_id)

        resp = self.auth_client.get(reverse("list_dynamic_attendances_statistics", kwargs={"type": "student"}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "daily"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "yearly"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "stream"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "class"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "gender"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "monthly"}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "school"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "village"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # print(resp.json())
        #
        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "school"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # print(resp.json())

        resp = self.client.get(reverse("list_create_attendance_statistics", kwargs={"type": "stream"}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # print(resp.json())
