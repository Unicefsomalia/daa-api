from django.test import tag
from rest_framework import status
from rest_framework.reverse import reverse

from client.models import MyUser
from core.tests import BaseAPITest
from school.models import Student, Stream, StudentReactivation


class StudentTests(BaseAPITest):
    @tag("createStud")
    def test_creating_student(self):
        stream_id = 1
        resp = self.create_student(first_name="TeStudent", last_name="1", stream=stream_id)
        # print(resp.data[0]["school_name"])
        # print(resp.json())
        student_id = resp.json()[0]["id"]
        # print(student_id)
        # print(ser.data)
        self.assertEquals(resp.status_code, status.HTTP_201_CREATED)

        resp = self.auth_client.get("{}".format(reverse("list_create_students")))

        self.assertEquals(resp.data["count"], 8)
        # print("All....", resp.data["count"])
        # for stud in resp.data["results"]:
        #     print(stud["first_name"],stud["middle_name"],stud["last_name"])
        #
        # print(resp.json()["results"])
        resp = self.auth_client.get("{}?name=mi ke".format(reverse("list_create_students")))
        self.assertEquals(resp.data["count"], 2)
        # print("FILTERED....", resp.data["count"])
        # for stud in resp.data["results"]:
        #     print(stud)
        #
        # for stud in resp.data["results"]:
        #     print(stud["first_name"], stud["middle_name"], stud["last_name"])
        school_emis_code = Stream.objects.get(id=stream_id).school.emis_code
        user = MyUser.objects.get(username=school_emis_code)
        self.set_authenticated_user(user.id)
        resp = self.auth_client.get(reverse("user_teacher_school_info"))
        # print(stream_id, school_emis_code)
        # print(resp.json())
        student = resp.json()["streams"][0]["students"][0]
        fields = ["village_name", "district_name", "region_name", "guardian_village_name", "guardian_district_name", "guardian_region_name", "guardian_status_display"]
        # for field in student:
        #   print(field,student[field])
        for field in fields:
            # print(student[field])
            is_available = field in student
            if not field in student:
                print(field)
            self.assertTrue(is_available)

        # print(student)

    def test_listing_absent_students(self):
        resp = self.create_student_absent_reason(description="TeStudentAbsentReason", student=2, date="2019-09-09")
        # print(resp.json())
        url = "{}?page_size=10&date=2019-09-09".format(reverse("list_absent_students"))
        # print(url)
        resp = self.auth_client.get(url)
        # print(resp.json())
        self.assertEquals(resp.status_code, 200)
        # print(resp.json())

    def test_listing_students(self):
        self.set_authenticated_user(2)
        resp = self.auth_client.get(reverse("list_create_students"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_student(self):
        # Id 2 beacause id is automatically created on creating a student
        resp = self.auth_client.get(reverse("retrieve_update_destroy_student", kwargs={"pk": 1}))
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["first_name"], "TheStudent")

    @tag("us")
    def test_updating_student(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_student", kwargs={"pk": 1}), data={"first_name": "Hello"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

        resp = self.auth_client.patch(
            reverse("retrieve_update_destroy_student", kwargs={"pk": 1}),
            data={
                "first_name": "Hello",
                "father_status": "A",
                "father_name": "Mia",
                "father_phone": "98999",
            },
        )

        print(resp.data["father_name"], resp.data["mother_name"], resp.data["guardian_name"])
        print(resp.data["father_phone"], resp.data["mother_phone"], resp.data["guardian_phone"])
        self.assertEquals(resp.data["first_name"], "Hello")
        print(resp.data["current_guardian_name"], "Hello")
        print(resp.data["current_guardian_phone"], "Hello")

    @tag("ds")
    def test_deleting_student(self):
        resp = self.create_delete_reason(name="error")
        error_delete_id = resp.json()["id"]
        student_id = 1
        resp = self.auth_client.delete("{}?reason=1&description=Nothing happens".format(reverse("retrieve_update_destroy_student", kwargs={"pk": student_id})))
        print(resp.data)
        self.assertEquals(resp.status_code, 204)

        resp = self.auth_client.get(reverse("list_dropout_students"))
        self.assertEquals(resp.data["count"], 1)
        # print(resp.json())

        resp = self.auth_client.patch("{}?description=Back To School".format(reverse("retrieve_reactivate_student", kwargs={"pk": student_id})))
        self.assertEquals(resp.status_code, 400)

        data = {"stream": 1, "reason": "Back to school"}
        resp = self.auth_client.patch("{}?description=Back To School".format(reverse("retrieve_reactivate_student", kwargs={"pk": student_id})), data=data)
        print(resp.json())
        self.assertEquals(resp.status_code, 200)

        self.assertAlmostEquals(StudentReactivation.objects.count(), 1)

        resp = self.auth_client.delete("{}?reason={}&description=Nothing happens".format(reverse("retrieve_update_destroy_student", kwargs={"pk": student_id}), error_delete_id))
        # print(resp.data)

        # resp = self.auth_client.patch("{}?description=Back To School".format(reverse("retrieve_reactivate_student", kwargs={"pk": student_id})), data=data)
        # print(resp.json())
        # self.assertEquals(resp.status_code, 404)
        # self.assertEquals(resp.json()["detail"], "Not found.")

        # print(resp.json())

    def test_creating_bulk_students(self):
        first_name = "TheStudent"
        stream = 1
        date_enrolled = "2019-06-06"
        last_name = "lastName"
        st1 = {"active": True, "special_needs": [1, 2], "first_name": first_name, "stream": stream, "date_enrolled": date_enrolled, "last_name": last_name}
        data = [st1, st1]
        resp = self.auth_client.post(reverse("list_create_bulk_students"), data=data, format="json")
        # print(resp.json())
        self.assertEquals(resp.status_code, 201)

    @tag("ldst", "ldst1")
    def test_listing_dynamic_test_id_guardin(self):
        stud_id = 1
        Student.objects.filter(id=stud_id).update(gender="F")
        stud = Student.objects.get(id=stud_id)
        # print(stud.live_with_parent)
        # print(stud.father_name, stud.mother_name, stud.guardian_name)
        # print(stud.father_phone, stud.mother_phone, stud.guardian_phone)
        url = reverse("list_dynamic_students_statistics", kwargs={"type": "id"})
        resp = self.auth_client.get(f"{url}?gender=F")
        print(resp.json())
        stud = resp.json()["results"][0]
        self.assertEquals(stud["current_guardian_relationship"], "Father")
        self.assertIn("current_guardian_phone",stud)
        self.assertIn("current_guardian_name",stud)

        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("ldst", "ldst2")
    def test_listing_dynamic_test_guardian_info_father(self):
        stud_id = 1
        Student.objects.filter(id=stud_id).update(
            gender="F",
            live_with_parent=True,
            guardian_name="Well",
            guardian_phone="08932",
            father_name="Mich",
            father_phone="0838768326",
        )
        stud = Student.objects.get(id=stud_id)
        # print(stud.live_with_parent)
        # print(stud.father_name, stud.mother_name, stud.guardian_name)
        # print(stud.father_phone, stud.mother_phone, stud.guardian_phone)
        url = reverse("list_dynamic_students_statistics", kwargs={"type": "id"})
        resp = self.auth_client.get(f"{url}?gender=F")
        # print(resp.json())
        stud = resp.json()["results"][0]
        self.assertEquals(stud["current_guardian_relationship"], "Father")
        self.assertEquals(stud["current_guardian_phone"], "0838768326")
        self.assertEquals(stud["current_guardian_name"], "Mich")

        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("ldst", "ldst2")
    def test_listing_dynamic_test_guardian_info_mother(self):
        stud_id = 1
        Student.objects.filter(id=stud_id).update(
            gender="F",
            live_with_parent=True,
            guardian_name="Well",
            guardian_phone="08932",
            mother_name="Liz",
            mother_phone="23252552",
        )
        stud = Student.objects.get(id=stud_id)
        # print(stud.live_with_parent)
        # print(stud.father_name, stud.mother_name, stud.guardian_name)
        # print(stud.father_phone, stud.mother_phone, stud.guardian_phone)
        url = reverse("list_dynamic_students_statistics", kwargs={"type": "id"})
        resp = self.auth_client.get(f"{url}?gender=F")
        # print(resp.json())
        stud = resp.json()["results"][0]
        self.assertEquals(stud["current_guardian_relationship"], "Father")
        self.assertIn("current_guardian_phone",stud)
        self.assertIn("current_guardian_name",stud)

        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("ldst")
    def test_listing_dynamic_test(self):
        resp = self.auth_client.get(reverse("list_dynamic_students_statistics", kwargs={"type": "gender"}))
        print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    @tag("st")
    def test_students_enrollments(self):
        resp = self.auth_client.get(reverse("list_students_enrollments", kwargs={"type": "class"}))
        # print(resp.json())
        self.assertEquals(resp.status_code, 200)
        resp = self.auth_client.get(reverse("list_students_enrollments", kwargs={"type": "month"}))
        self.assertEquals(resp.status_code, 200)

        resp = self.auth_client.get(reverse("list_students_enrollments", kwargs={"type": "year"}))
        self.assertEquals(resp.status_code, 200)

        resp = self.auth_client.get(reverse("list_students_enrollments", kwargs={"type": "school"}))
        self.assertEquals(resp.status_code, 200)

        resp = self.auth_client.get(reverse("list_students_enrollments", kwargs={"type": "gender"}))
        self.assertEquals(resp.status_code, 200)

        resp = self.auth_client.get(reverse("list_students_enrollments", kwargs={"type": "school"}))
        # print(resp.json())
        self.assertEquals(resp.status_code, 200)

        # print(resp.json())
