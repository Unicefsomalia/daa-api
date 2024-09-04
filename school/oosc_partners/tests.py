
from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from django.test import tag
import school.models as school_models
import attendance.models as att_models
class OoscPartnerTests(BaseAPITest):
    
    def setUp(self):
        super(OoscPartnerTests,self).setUp()

    @tag("cop")
    def test_creating_oosc_partner(self):
        resp = self.create_oosc_partner(name="madC2",email="michameiu@gmail.com")
        # print(resp.json())
        resp = self.create_oosc_partner(name="madC",email="m@gla.com")
        # print(resp.json())
        self.assertEquals(resp.status_code, 400)
        
        

    def test_listing_oosc_partner(self):
        resp = self.auth_client.get(reverse("list_create_oosc_partners"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_oosc_partner(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_oosc_partner", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC")
    
    @tag("pft")
    def test_partner_filters(self):
        url = reverse("list_dynamic_students_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&has_partner=false")
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["count"], 0)
        
        resp = self.auth_client.get(f"{url}?export=false&has_partner=true")
        # print(resp.json())
        student=resp.json()["results"][0]
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertIn("name",student)
        self.assertIn("email",student)
        self.assertEquals(student["name"],"madC")
        self.assertEquals(student["email"],"micha@micah.com")
        
        
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&has_partner=true")
        # print(resp.json())
        count=resp.json()["count"]
        attendance=resp.json()["results"][0]
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertIn("name",attendance)
        self.assertIn("email",attendance)
        self.assertEquals(student["name"],"madC")
        self.assertEquals(student["email"],"micha@micah.com")
        
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&has_partner=false")
        # print(resp.json())
        count=resp.json()["count"]
        self.assertEquals(count,0)
        
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "village"})
        
        resp = self.auth_client.get(f"{url}?export=false&has_partner=true")
        print(resp.json())

    @tag("cop","copu")
    def test_updating_oosc_partner(self):
        email="micha@micah.com"
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_oosc_partner", kwargs={"pk": 1}), data={"name": "madC3","email":email})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC3")
        
        email="micha38776@micah.com"
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_oosc_partner", kwargs={"pk": 1}), data={"name": "madC3","email":email})
        # print(resp.json())
        self.assertEquals(resp.data["email"], email)
        
        resp=self.get_token(username=email,password="admin")
        # print(token.status_code)
        # print(token.json())
        self.assertEquals(resp.status_code,200)
        
        res=self.create_stream(name="B",base_class="2",school=2)
        stream_id=res.json()["id"]
        # print(res.json())
        school_models.Student.objects.filter(id=3).update(stream_id=stream_id)
        
        
        self.take_attendance(date="2024-10-11",absent=[4])
        resp=self.take_attendance(date="2024-10-10",absent=[3,2],stream=stream_id)
        # print(resp.json())
        
        # print(att_models.Attendance.objects.filter(stream__school_id=2).count())
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false")
        # print(resp.json())
        count=resp.json()["count"]
        self.assertEquals(count,1)
        attendance=resp.json()["results"][0]
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertIn("name",attendance)
        self.assertIn("email",attendance)
        
        self.create_oosc_partner(name="M2",email="m@gmail.com",schools=[])
        
        
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&partner=2")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        count=resp.json()["count"]
        # print(resp.json())
        self.assertEquals(count,0)
        
        
        
        url = reverse("list_dynamic_students_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false")
        # print(resp.json())
        student=resp.json()["results"][0]
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertIn("name",student)
        self.assertIn("email",student)
        
        url = reverse("list_dynamic_students_statistics", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&partner=2")
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        count=resp.json()["count"]
        # print(resp.json())
        self.assertEquals(count,0)
        
        url = reverse("list_create_schools_stats", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&has_partner=false")
        # print(resp.json())
        count=resp.json()["count"]
        self.assertEquals(count,1)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        
        url = reverse("list_create_schools_stats", kwargs={"type": "partner"})
        resp = self.auth_client.get(f"{url}?export=false&has_partner=true")
        # print(resp.json())
        partner=resp.json()["results"][0]
        count=resp.json()["count"]
        self.assertEquals(count,1)
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(partner["name"],"madC3")
        
