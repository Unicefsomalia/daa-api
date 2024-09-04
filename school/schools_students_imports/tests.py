from os import path

import openpyxl
from django.test import tag
from openpyxl import Workbook
from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from school.models import Student
from django.contrib.staticfiles import finders


def create_an_empty_workbook(rows_count):
    # headers=["school","school nemis code","county","subcounty","first name","last name","gender","class","special_needs",
    #          "status","guardian name","guardian county","guardian subcounty","guardian email","date_enrolled"]
    pass


class SchoolsStudentsImportTests(BaseAPITest):
    def create_schools_students_import(
        self,
        user="1",
        step="Q",
        rows_count="1",
        imported_rows_count="1",
        name="madC",
        file_name="test_excel.xlsx",
        should_import=True,
    ):
        filePath = finders.find(file_name)
        # print(filePath)
        with open(filePath, "rb") as import_file:
            data = {
                "user": user,
                "step": step,
                "rows_count": rows_count,
                "imported_rows_count": imported_rows_count,
                "name": name,
                "import_file": import_file,
                "should_import": should_import,
            }
            return self.auth_client.post(
                reverse("list_create_schools_students_imports"),
                data=data,
                format="multipart",
            )

    def setUp(self):
        super(SchoolsStudentsImportTests, self).setUp()
        print(Student.objects.all().count())
        # resp = self.create_schools_students_import()
        # print(resp.json())

    @tag("tis")
    def test_simple_file(self):
        students_count_before = Student.objects.count()
        resp = self.create_schools_students_import()
        students_count_after = Student.objects.count()
        # shoulde be 6, 18
        # print("Before", students_count_before, "After", students_count_after)
        self.assertGreater(students_count_after,students_count_before)

    @tag("saaman")
    def test_saaman(self):
        resp = self.create_schools_students_import(name="madC", file_name="saaman.xlsx")
        print(resp.json())
    
    
    @tag("qaydaro")
    def test_qaydaro(self):
        resp = self.create_schools_students_import(name="madC", file_name="qaydaro.xlsx")
        print(resp.json())
        
    @tag("cicq")
    def test_creating_schools_students_import(self):
        pre__pre_import_coint = Student.objects.all().count()

        resp = self.create_schools_students_import(name="madC", should_import=False)
        # print(resp.json())

        resp = self.create_schools_students_import(
            name="madC",
        )

        pre_import_coint = Student.objects.all().count()

        resp = self.create_schools_students_import(name="madC", file_name="main_sample.xlsx")

        # print(resp.json())
        resp = self.auth_client.get(reverse("retrieve_update_destroy_schools_students_import", kwargs={"pk": resp.json()["id"]}))
        # print(resp.json())
        # for data in resp.json()["results"]:
        #     # print(data)
        #     print("")
        #     pass
        # self.assertEquals(resp.status_code, status.HTTP_201_CREATED)
        print("pre__pre_import_coint=", pre__pre_import_coint, "pre_import_coint", pre_import_coint, Student.objects.all().count())
        self.assertEquals(Student.objects.all().count(), 22)

    def test_listing_schools_students_import(self):
        resp = self.auth_client.get(reverse("list_create_schools_students_imports"))
        # print(resp.json())
        # self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_schools_students_import(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_schools_students_import", kwargs={"pk": 1}))
        # print(resp.json())
        # self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # self.assertEquals(resp.data["name"], None)

    def test_updating_schools_students_import(self):
        resp = self.auth_client.patch(
            reverse("retrieve_update_destroy_schools_students_import", kwargs={"pk": 1}),
            data={"name": "madC"},
        )
        # self.assertEquals(resp.status_code, status.HTTP_200_OK)
        # self.assertEquals(resp.data["name"], "madC")
