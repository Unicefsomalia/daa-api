import os
import shutil
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient
import school.models as school_models
from attendance.models import Attendance
from client.models import MyUser
from school.models import Student
from oauth2_provider.models import Application

from django.conf import settings
class BaseAPITest(APITestCase):
    username = "michameiu@gmail.com"
    password = "micha"
    client_id = "iuyutyutuyctua"
    client_secret = "lahkckagkegigciegvjegvjhv"
    speaker = None

    def setUp(self):
        self.deletePreviousMedia()
        user = MyUser.objects.create(username=self.username)
        self.client = APIClient()
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=user)
        self.user = user
        self.user.set_password(self.password)
        self.user.save()
        
        app = Application()
        app.client_id = self.client_id
        app.user = self.user
        app.authorization_grant_type = "password"
        app.client_type = "public"
        app.client_secret = self.client_secret
        app.save()

        ####Create a hospital staff Staff Amdin #user id 2
        resp = self.create_user()
        # print(resp.json())
        self.assertEqual(resp.status_code, 401)

        resp = self.create_state()

        resp = self.create_region()

        resp = self.create_district()

        # resp = self.create_county()

        resp = self.create_village()

        resp = self.create_special_need()
        resp = self.create_special_need(name="Health")

        resp = self.create_school()
        resp = self.create_school(name="SCh2", emis_code="PADD")
        self.create_oosc_partner()

        resp = self.create_teacher()
        resp = self.create_stream()
        # resp = self.create_stream(base_class="3")
        resp = self.create_stream(name="North", base_class="8")
        stresp = self.create_stream(name="North", base_class="5", school=2)
        # print(resp.json())
        resp = self.create_student()
        resp = self.create_student(first_name="Miah", stream=3)
        # print(resp.json())
        resp = self.create_delete_reason()
        resp = self.take_attendance()
        resp = self.create_support_question()
        resp = self.create_absent_reason()
        resp = self.create_student_absent_reason()

        
        

        # print(resp.json())

        # print(resp.json())

    def deletePreviousMedia(self):
        # Delete all files in the media folder
        # print("deleting previous media.")
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))

    def school_2_take_attendance(self):
        res=self.create_stream(name="B",base_class="2",school=2)
        stream_id=res.json()["id"]
        # print(res.json())
        school_models.Student.objects.filter(id=3).update(stream_id=stream_id)
        
        self.take_attendance(date="2024-10-11",absent=[4])
        resp=self.take_attendance(date="2024-10-10",absent=[3,2],stream=stream_id)
        
    def create_custom_export(self,list_size=5, name="monthly",custom_report_name="new_user", title="Hello Somalia", description="Okay there", start_date="2010-01-01", end_date="2030-01-01"):
        data = {"name": name,"list_size":list_size,"custom_report_name":custom_report_name, "title": title, "description": description,"start_date":start_date,"end_date":end_date}
        return self.auth_client.post(reverse("list_create_custom_exports"), data=data)
    
    def create_oosc_partner(self, name="madC" , email="micha@micah.com" , schools="1" ):
        data={  "name":name , "email":email , "schools":[schools]  }
        return self.auth_client.post(reverse("list_create_oosc_partners"),data=data,format="json")


    def create_translation_text(self, title="madC", example="1"):
        data = {"title": title, "example": example}
        return self.auth_client.post(reverse("list_create_translation_texts"), data=data)

    def create_translation_locale(self, name="Somali", country_code="SO", language_code="so"):
        data = {"name": name, "country_code": country_code, "language_code": language_code}
        return self.auth_client.post(reverse("list_create_translation_locales"), data=data)

    def create_state(self, name="madC"):
        data = {"name": name}
        return self.auth_client.post(reverse("list_create_states"), data=data)

    def create_village(self, district="1", name="madC"):
        data = {"district": district, "name": name}
        return self.auth_client.post(reverse("list_create_villages"), data=data)

    def create_special_need(self, name="madC"):
        data = {"name": name}
        return self.auth_client.post(reverse("list_create_special_needs"), data=data)

    def create_county(self, name="madC"):
        data = {"name": name}
        return self.auth_client.post(reverse("list_create_countys"), data=data)

    def create_region(
        self,
        name="TheRegion",
        state="1",
    ):
        data = {"name": name, "state": state}
        return self.client.post(reverse("list_create_regions"), data=data)

    def create_user(self):
        user = {"first_name": "Test", "last_name": "Doe", "username": "mfa", "password": "m", "role": "SCHT"}
        return self.client.post(reverse("list_create_system_users"), user)

    def get_token(self, username="kel", password="m"):
        # user={"username":"kel","password":"m","client_id":self.client_id,"grant_type":"password"}
        user = "username={2}&password={1}&client_id={0}&grant_type=password".format(self.client_id, password, username)
        cl = APIClient()
        return cl.post("/o/token/", user, content_type="application/x-www-form-urlencoded")


    def set_authenticated_user(self, user_id=2):
        self.auth_client.force_authenticate(user=MyUser.objects.get(id=user_id))

    # def create_village(self, name="The village", district=1):
    #     data = {"name": name, "district": district, "lat": -1.323323, "lng": 36.434}
    #     return self.auth_client.post(reverse("list_create_villages"), data=data)

    def create_district(self, name="TheDistrict", region=1):
        data = {"name": name, "region": region}
        return self.auth_client.post(reverse("list_create_districts"), data=data)

    def create_school(self, name="TheSchool", emis_code="345"):
        data = {"name": name, "emis_code": emis_code, "village": 1}
        return self.auth_client.post(reverse("list_create_schools"), data=data)

    def create_teacher(self, streams=None, first_name="TheTeacher", last_name="Micha", phone="675", school=1):
        data = {"first_name": first_name, "is_school_admin": False if streams != None else True, "phone": phone, "school": school, "last_name": last_name}
        if streams != None:
            data["streams"] = streams
        return self.auth_client.post(reverse("list_create_teachers"), data=data)

    def create_stream(self, name="TheStream", base_class="7", school=1):
        data = {"school": school, "base_class": base_class}
        if name != None:
            data["name"] = name
        return self.auth_client.post(reverse("list_create_streams"), data=data)

    def create_student(
        self,
        first_name="TheStudent",
        stream=1,
        moe_extra_info={"district_id": 10, "state_id": 11, "region_id": 12, "blood_group_id": 13, "section_id": 14},
        date_enrolled="2019-06-06",
        admission_no=123,
        status="PE",
        guardina_name="Micha",
        guardian_phone="072267537",
        last_name="lastName",
        guardian_relationship="Uncle",
        live_with_parent=False,
    ):
        std1 = {
            "active": True,
            "special_needs": [1],
            "status":status,
            "guardian_relationship": guardian_relationship,
            "live_with_parent": live_with_parent,
            "moe_extra_info": moe_extra_info,
            "first_name": first_name,
            "admission_no": admission_no,
            "stream": stream,
            "date_enrolled": date_enrolled,
            "last_name": last_name,
            "guardian_name": guardina_name,
            "guardian_phone": guardian_phone,
        }
        std2 = {"active": True, "special_needs": [1], "moe_extra_info": moe_extra_info, "first_name": first_name, "stream": stream, "date_enrolled": date_enrolled, "last_name": last_name}
        data = [std1, std2]
        return self.auth_client.post(reverse("list_create_bulk_students"), data=data, format="json")

    def take_attendance_for_student(self, date="2019-09-20", stream=1, student=1):
        dat = {"date": date, "present": [student], "absent": [], "stream": stream}
        data = [dat]
        return self.auth_client.post(reverse("list_create_attendances"), data=data, format="json")

    def take_attendance(self, date="2019-09-09", present=[1], absent=[2], stream=1):
        # print(Student.objects.get(id=1))
        self.create_student(first_name="micgha", last_name="kelvin")
        dat = {"date": date, "present": present, "absent": absent, "stream": stream}
        data = [dat]
        return self.auth_client.post(reverse("list_create_attendances"), data=data, format="json")

    def create_delete_reason(self, name="TheDeleteReason"):
        data = {"name": name}
        return self.auth_client.post(reverse("list_create_delete_reasons"), data=data)

    def create_support_question(self, title="TheSupportQuestion"):
        data = {"title": title, "description": "Go to hell"}
        return self.auth_client.post(reverse("list_create_support_questions"), data=data)

    def create_absent_reason(self, name="TheAbsentReason"):
        data = {"name": name}
        return self.auth_client.post(reverse("list_create_absent_reasons"), data=data)

    def create_student_absent_reason(self, description="TheStudentAbsentReason", reason=1, student=1, date="2019-05-09"):
        data = {"student": student, "reason": reason, "description": description, "date": date}
        url = reverse("list_create_student_absent_reasons")
        return self.auth_client.post(url, data=data)
