import datetime
from os import path
from pyexpat import model
import re
from statistics import mode
from core.common import default_enabled_filter
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Case, When, Value, Max, Min
from django.db.models.functions import Concat, ExtractMonth, ExtractDay, ExtractYear, Trunc, TruncDate, Coalesce, TruncDay

# Create your models here.
from django.db.models import F, Value, DateField, Count, Q, CharField
from django.db.models.expressions import RawSQL
from django.db.models.functions import Concat, Trunc, TruncDate, Coalesce
from django.utils import timezone
from multiselectfield import MultiSelectField

from client.models import MyUser, MyUserRoles
from mylib.my_common import MyModel, case_generator
from mylib.mygenerics import GroupConcat
from core.common import get_student_current_guardian
from region.models import Village, SubCounty
from django.utils.dateparse import parse_date
from somapi.settings import MEDIA_ROOT




SPECIAL_NEEDS = (
    ("N", "None"),
    ("V", "Visual"),
    ("H", "Hearing"),
    ("P", "Physical"),
    ("L", "Learning"),
)

CLASSES = (
    ("0", "ECD"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
    ("6", "6"),
    ("7", "7"),
    ("8", "8"),
)


class School(MyModel):
    # public,private,community,idp
    LOCATION = (
        ("PBC", "Rural"),
        ("PRV", "Urban"),
        ("CMY", "Community"),
        ("IDP", "Internally Displaced Person"),
    )
    GENDER = (
        ("M", "Boys"),
        ("F", "Girls"),
        ("MX", "Mixed"),
    )
    BOARDING = (("D", "Day Only"), ("B", "Boarding Only"), ("BD", "Boarding and Day"))
    village = models.ForeignKey(Village, null=True, related_name="schools", blank=True, on_delete=models.SET_NULL)
    name = models.CharField( max_length=45)
    emis_code = models.CharField(unique=True, max_length=45)
    phone = models.CharField(null=True, blank=True, max_length=30)
    email = models.EmailField(max_length=100, null=True, blank=True)
    school_ministry = models.CharField(max_length=100, null=True, blank=True)
    founder_name = models.CharField(max_length=70, null=True, blank=True)
    year_of_foundation = models.DateField(null=True, blank=True)
    location_type = models.CharField(max_length=5, null=True, blank=True, choices=LOCATION)
    location = models.CharField(max_length=45, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    start_of_calendar = models.DateField(null=True, blank=True)
    end_of_calendar = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    lowest_grade = models.CharField(default="P1", max_length=4, choices=CLASSES)
    highest_grade = models.CharField(default="P8", max_length=4, choices=CLASSES)
    schooling = models.CharField(default="D", max_length=4, choices=BOARDING)
    gender = models.CharField(default="MX", max_length=4, choices=GENDER)
    moe_id = models.CharField(null=True, blank=True, max_length=50)
    moe_emis_code = models.CharField(null=True, blank=True, max_length=50)
    is_training_school = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)

    @staticmethod
    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: "id",
            MyUserRoles.NGO.name: "id",
            MyUserRoles.SCHT.name: "id",
            MyUserRoles.VLGA.name: "village_id",
            MyUserRoles.DSTA.name: "village__district_id",
            MyUserRoles.RGNA.name: "village__district__region_id",
        }


SCHOOL_REGION_NAME = F("village__district__region__name")
SCHOOL_DISTRICT_NAME = F("village__district__name")
SCHOOL_VILLAGE_NAME = F("village__name")

SCHOOL_SUB_COUNTY_NAME = F("sub_county__name")
SCHOOL_COUNTY_NAME = F("sub_county__county__name")

SCHOOL_STATS_DEFINITIONS = {
    "id": {
        "value": F("id"),
        "extra_fields": {
            "village_name": SCHOOL_VILLAGE_NAME,
            "district_name": SCHOOL_DISTRICT_NAME,
            "region_name": SCHOOL_REGION_NAME,
            "day_boarding": F("schooling"),
        },
        "resp_fields": {"id", "name", "emis_code", "email", "lat", "lng"},
    },
    "village": {
        "value": F("village_id"),
        "extra_fields": {
            "village_name": SCHOOL_VILLAGE_NAME,
            "district_name": SCHOOL_DISTRICT_NAME,
            "region_name": SCHOOL_REGION_NAME,
        },
    },
     "partner":{
      "value":F("partners__id"),
      "extra_fields":{
          "name":F("partners__name"),
          "email":F("partners__email"),
      }
    }, 
    "district": {
        "value": F("village__district_id"),
        "extra_fields": {
            "county_name": SCHOOL_DISTRICT_NAME,
        },
    },
    "region": {
        "value": F("village__district__region_id"),
        "extra_fields": {
            "county_name": SCHOOL_REGION_NAME,
        },
    },
}

DEFAULT_SCHOOL_FIELDS = {}


class SpecialNeed(MyModel):
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


CLASSES_MAP = {c[0]: c[1] for c in CLASSES}


class Stream(MyModel):
    school = models.ForeignKey(School, related_name="streams", on_delete=models.CASCADE)
    name = models.CharField(max_length=45, default="", null=True, blank=True)
    last_attendance = models.DateField(null=True, blank=True)
    base_class = models.CharField(choices=CLASSES, default="1", max_length=3)
    moe_id = models.CharField(null=True, blank=True, max_length=50)
    moe_section_id = models.CharField(max_length=45, null=True, blank=True)
    moe_name = models.CharField(max_length=45, null=True, blank=True)
    moe_section_name = models.CharField(max_length=45, null=True, blank=True)
    active = models.BooleanField(default=True, editable=False)

    # moe_extra_info=models.JSONField(editable=False,null=True,blank=True)

    @property
    def class_name(self):
        name = self.name if self.name != None else ""
        try:
            
            if self.moe_name:
                return "{} {}".format(self.moe_name, name)
            return "{} {}".format(CLASSES_MAP[self.base_class], name)
        except Exception as e:
            return f"{self.base_class} {name}"
            
        
    @property
    def full_class_name(self):
        return "{} - Class {}".format(self.school.name, self.class_name)

    def __str__(self):
        return "CLASS {}".format(self.class_name)

    class Meta:
        ordering = ("id",)
        # unique_together=("school","name")

    @staticmethod
    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: "school_id",
            MyUserRoles.SCHT.name: "school_id",
            MyUserRoles.NGO.name: "school_id",
            MyUserRoles.VLGA.name: "school__village_id",
            MyUserRoles.DSTA.name: "school__village__district_id",
            MyUserRoles.RGNA.name: "school__village__district__region_id",
        }

    def attendance_taken(self, date):
        date = parse_date(date)
        # print("Updating the attendance Date %s"%(date))
        if self.last_attendance == None:
            # print("NO last attendance.")
            self.last_attendance = date
        elif date > self.last_attendance:
            # print("New last attendance.")
            self.last_attendance = date
        else:
            pass
            # print("Just confused.")
        self.save()
        # print("Final date %s" %(self.last_attendance))


class OoscPartner(MyModel):
    name=models.CharField(max_length=105,unique=True)
    email=models.EmailField(max_length=100)
    schools=models.ManyToManyField(School,related_name="partners",)
    user=models.OneToOneField(MyUser,related_name="partner",editable=False,null=True,blank=True,on_delete=models.CASCADE)
    
    class Meta:
        ordering=("name",)
        
    def __str__(self):
        return self.name
    

class Teacher(MyModel):
    TEACHER_TYPE = (("E", "Employed"), ("V", "Volunteer"))
    QUALIFICATIONS = (("NS", "Not Set"), ("UNI", "UNIVERSITY"), ("COL", "COLLEGE"))
    first_name = models.CharField(max_length=45)
    middle_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45)
    user = models.OneToOneField(MyUser, null=True, blank=True, related_name="teacher", on_delete=models.SET_NULL)
    date_started_teaching = models.DateField(null=True, blank=True)
    joined_current_school = models.DateField(null=True, blank=True)
    is_non_delete = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    type = models.CharField(max_length=3, choices=TEACHER_TYPE, default="E")
    employment_id = models.CharField(max_length=45, null=True, blank=True)
    employed_by = models.CharField(max_length=45, null=True, blank=True) 
    partner=models.ForeignKey(OoscPartner,related_name="teachers", null=True, blank=True,on_delete=models.SET_NULL)
    
    phone = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey(School, related_name="teachers", on_delete=models.CASCADE)
    streams = models.ManyToManyField(Stream, null=True, blank=True, related_name="teachers")
    qualifications = models.CharField(max_length=3, choices=QUALIFICATIONS, default="NS", null=True, blank=True)
    is_school_admin = models.BooleanField(default=False)
    email = models.EmailField(max_length=100, null=True, blank=True)
    MARITAL_STATUS = (
        ("NS", "Not Set"),
        ("S", "Single"),
        ("M", "Married"),
        ("D", "Divorced"),
    )
    marital_status = models.CharField(max_length=3, choices=MARITAL_STATUS, default="NS")
    dob = models.DateField(null=True, blank=True)
    moe_id = models.CharField(null=True, blank=True, max_length=50)

    def __str__(self):
        return "{} {} {}".format(self.first_name, self.last_name, self.school.name)

    class Meta:
        ordering = ("id",)

    @property
    def full_name(self):
        names = []
        if self.first_name:
            names.append(self.first_name)
        if self.middle_name:
            names.append(self.middle_name)
        if self.last_name:
            names.append(self.last_name)
        return " ".join(names)

    @staticmethod
    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: "school_id",
            MyUserRoles.SCHT.name: "school_id",
            MyUserRoles.NGO.name: "school_id",
            MyUserRoles.VLGA.name: "school__village_id",
            MyUserRoles.DSTA.name: "school__village__district_id",
            MyUserRoles.RGNA.name: "school__village__district__region_id",
        }


TECH_FULL_NAME = Concat(
    Coalesce("first_name", Value("")),
    Value(" "),
    Coalesce("middle_name", Value("")),
    Value(" "),
    Coalesce("last_name", Value("")),
)
TECH_SCHOOL_NAME = F("school__name")
TECH_DISTRICT_NAME = F("school__village__district__name")
TECH_REGION_NAME = F("school__village__district__region__name")
TECH_SHEHIYA_NAME = F("school__village__name")
TEACHER_STATS_DEFINITIONS = {
    "id": {
        "value": F("id"),
        "extra_fields": {
            "full_name": TECH_FULL_NAME,
            "school_name": TECH_SCHOOL_NAME,
            "joined_date": F("joined_current_school"),
            "username": F("phone"),
            "village_name": TECH_SHEHIYA_NAME,
            "district_name": TECH_DISTRICT_NAME,
            "region_name": TECH_REGION_NAME,
        },
        "resp_fields": {"id", "employment_id"},
    },
    "village": {
        "value": F("village_id"),
        "extra_fields": {
            "village_name": TECH_SHEHIYA_NAME,
            "region_name": TECH_REGION_NAME,
            "district_name": TECH_DISTRICT_NAME,
        },
    },
    "district": {
        "value": F("school__village__district_id"),
        "extra_fields": {
            "region_name": TECH_REGION_NAME,
            "district_name": TECH_DISTRICT_NAME,
        },
    },
    
    "region": {
        "value": F("school__village__district__region_id"),
        "extra_fields": {
            "region_name": TECH_REGION_NAME,
        },
    },
}

DEFAULT_TEACHER_FIELDS = {
    "employed": Count("id", filter=Q(type="E")),
    "volunteer": Count("id", filter=Q(type="V")),
}


class GraduatesStream(MyModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="graduate_streams")
    year = models.PositiveSmallIntegerField(max_length=4)
    name = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ("school", "year")

    def __str__(self):
        return self.school.name + "-" + str(self.year) + "-Graduates"


STUDENT_STATUS = (
    ("AE", "Already Enrolled"),
    ("NE", "Newly Enrolled"),
    ("PE", "Re-Enrolled"),
)
STUDENT_GENDERS = (("M", "MALE"), ("F", "FEMALE"))


PERSON_STATUS = (
    ("A", "Alive"),
    ("D", "Deceased"),
)

PRE_PRIMARY = (
    ("N", "None"),
    ("Q", "Quranic"),
    ("F", "Formal"),
)


class Student(MyModel):
    TRANSPORT = (
        ("PERSONAL", "Personal Vehicle"),
        ("BUS", "School Bus"),
        ("FOOT", "By Foot"),
        ("NS", "Not Set"),
    )
    TIME_TO_SCHOOL = (
        ("1HR", "One Hour"),
        ("-0.5HR", "Less than 1/2 Hour"),
        ("+1HR", "More than one hour."),
        ("NS", "Not Set"),
    )
    # LIVE_WITH = (('P', 'Parents'), ('G', 'Gurdians'), ('A', 'Alone'), ('NS', 'Not Set'))
    LIVE_WITH = (
        ("B", "Both Parents"),
        ("S", "Single Parent"),
        ("N", "None"),
        ("NS", "Not Set"),
    )

    # admission_no = models.BigIntegerField(null=True, blank=True)
    # school_id     = models.ForeignKey(Schools,on_delete = models.CASCADE)
    emis_code = models.BigIntegerField(null=True, blank=True)

    ##
    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, null=True, blank=True, help_text="Father's name")
    last_name = models.CharField(max_length=200, null=True, blank=True, help_text="Grand Father's name")
    family_nick_name = models.CharField(max_length=200, null=True, blank=True, help_text="Grand Father's name")

    date_of_birth = models.DateField(null=True, blank=True)
    date_enrolled = models.DateField(default=timezone.now)
    admission_no = models.CharField(max_length=50, null=True, blank=True)
    stream = models.ForeignKey(Stream, null=True, blank=True, on_delete=models.CASCADE, related_name="students")  # shows the current class
    gender = models.CharField(max_length=2, choices=STUDENT_GENDERS, default="M")
    previous_class = models.IntegerField(default=0, null=True, blank=True)
    mode_of_transport = models.CharField(max_length=20, default="NS", choices=TRANSPORT)
    time_to_school = models.CharField(max_length=50, default="NS", choices=TIME_TO_SCHOOL)
    distance_from_school = models.IntegerField(null=True, blank=True)
    household = models.IntegerField(default=0, null=True)  # people in the same house
    meals_per_day = models.IntegerField(default=0, null=True, blank=True)
    not_in_school_before = models.BooleanField(default=False)  # reason for not being in school before
    emis_code_histories = models.CharField(max_length=200, null=True, blank=True)
    total_attendance = models.IntegerField(default=0, null=True, blank=True)
    total_absents = models.IntegerField(default=0, null=True, blank=True)
    last_attendance = models.DateField(null=True, blank=True)
    knows_dob = models.BooleanField(default=True)

    # Parent Name
    father_name = models.CharField(max_length=50, null=True, blank=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_status = models.CharField(max_length=20, choices=PERSON_STATUS, null=True, blank=True)

    mother_name = models.CharField(max_length=50, null=True, blank=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_status = models.CharField(max_length=20, choices=PERSON_STATUS, null=True, blank=True)

    live_with_parent = models.BooleanField(default=False)

    guardian_name = models.CharField(max_length=50, null=True, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_status = models.CharField(max_length=20, choices=LIVE_WITH, default="NS")
    guardian_relationship = models.CharField(max_length=45, null=True, blank=True)
    # guardian_sub_county = models.ForeignKey(
    #     SubCounty,
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="students_guardians",
    # )
    # guardian_email = models.EmailField(null=True, blank=True, max_length=45)

    # sub_county = models.ForeignKey(SubCounty, null=True, blank=True, on_delete=models.SET_NULL)
    village = models.ForeignKey(Village, related_name="students", null=True, blank=True, max_length=45, on_delete=models.SET_NULL)
    guardian_village = models.ForeignKey(Village, related_name="students_guardians", null=True, blank=True, max_length=45, on_delete=models.SET_NULL)

    has_special_needs = models.BooleanField(default=False)

    active = models.BooleanField(default=True, editable=False)
    graduated = models.BooleanField(default=False)
    dropout_reason = models.CharField(max_length=200, null=True, blank=True)
    offline_id = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(choices=STUDENT_STATUS, max_length=5, default="NE")
    # special_needs=MultiSelectField(choices=SPECIAL_NEEDS,max_length=10,null=True,blank=True)
    special_needs = models.ManyToManyField(SpecialNeed, null=True, blank=True, related_name="students")
    graduates_class = models.ForeignKey(GraduatesStream, null=True, blank=True, on_delete=models.SET_NULL)
    moe_id = models.CharField(null=True, blank=True, max_length=50)
    moe_unique_id = models.CharField(null=True, blank=True, max_length=45)
    moe_extra_info = models.JSONField(null=True, blank=True)
    house_number = models.CharField(max_length=100, null=True, blank=True)
    street_name = models.CharField(max_length=100, null=True, blank=True)
    upi = models.CharField(max_length=45, null=True, blank=True, help_text="Unique Identification provided by the school")
    # Is it an out of school children
    ##
    is_over_age = models.BooleanField(default=False)
    # has_attended_pre_primary = models.BooleanField(default=True)

    pre_primary_attendend = models.CharField(max_length=3, choices=PRE_PRIMARY, null=True, blank=True)

    class Meta:
        ordering = ("id",)
        indexes = [
            models.Index(fields=["gender"], name="students_gender_indx"),
            models.Index(fields=["id", "gender"], name="students_id_gender_indx"),
        ]

    @staticmethod
    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: ["stream__school_id"],
            MyUserRoles.SCHT.name: "stream__school_id",
            MyUserRoles.NGO.name: "stream__school_id",
            MyUserRoles.VLGA.name: "stream__school__village_id",
            MyUserRoles.DSTA.name: "stream__school__village__district_id",
            MyUserRoles.RGNA.name: "stream__school__village__district__region_id",
        }

    def __str__(self):
        if self.stream:
            return self.first_name + "(" + self.stream.name + ")"
        return self.first_name

    @property
    def full_name(self):
        return "{} {} {}".format(
            self.first_name,
            self.middle_name if self.middle_name != None else "",
            self.last_name if self.last_name != None else "",
        )

    def get_current_guardian(self):
        if not self.live_with_parent:
            return "GRD"

        # if self.father_name and self.father_status == "A" and self.father_phone:
        #     return "FTH"
        # if self.mother_name and self.mother_status == "A" and self.mother_phone:
        #     return "MTH"

        # if self.father_name and self.father_status == "A":
        #     return "FTH"
        # if self.mother_name and self.mother_status == "A":
        #     return "MTH"

        if self.father_name and self.father_phone:
            return "FTH"
        if self.mother_name and self.mother_phone:
            return "MTH"

        if self.father_phone:
            return "FTH"
        if self.mother_phone:
            return "MTH"

        return "GRD"

    @property
    def current_guardian_relationship(self):
        guardin = self.get_current_guardian()
        if guardin == "FTH":
            return "Father"
        elif guardin == "MTH":
            return "Mother"
        return self.guardian_relationship

    @property
    def current_guardian_name(self):
        guardin = self.get_current_guardian()
        if guardin == "FTH":
            return self.father_name
        elif guardin == "MTH":
            return self.mother_name

        return self.guardian_name

    @property
    def current_guardian_phone(self):
        guardin = self.get_current_guardian()
        if guardin == "FTH":
            return self.father_phone
        elif guardin == "MTH":
            return self.mother_phone
        return self.guardian_phone

    @property
    def age(self):
        if self.date_of_birth:
            # Get today's date object
            today = datetime.today()

            # A bool that represents if today's day/month precedes the birth day/month
            one_or_zero = (today.month, today.day) < (
                self.date_of_birth.month,
                self.date_of_birth.day,
            )

            # Calculate the difference in years from the date object's components
            year_difference = today.year - self.date_of_birth.year

            # The difference in years is not enough.
            # To get it right, subtract 1 or 0 based on if today precedes the
            # birthdate's month/day.

            # To do this, subtract the 'one_or_zero' boolean
            # from 'year_difference'. (This converts
            # True to 1 and False to 0 under the hood.)
            age = year_difference - one_or_zero
            return age

    @property
    def student_id(self):
        return self.admission_no if self.admission_no != None else "XXX"
        if self.admission_no is None and self.upi is None:
            return "XXX / XXX"
        if self.admission_no is None and self.upi is not None:
            return "{} / XXX".format(self.upi)
        if self.admission_no is not None and self.upi is None:
            return "XXX / {}".format(self.admission_no)
        return "{} / {}".format(self.upi, self.admission_no)


STUDENT_SCHOOL_STATE_NAME = F("stream__school__village__district__region__state__name")
STUDENT_SCHOOL_REGION_NAME = F("stream__school__village__district__region__name")
STUDENT_SCHOOL_DISTRICT_NAME = F("stream__school__village__district__name")
STUDENT_SCHOOL_VILLAGE_NAME = F("stream__school__village__name")

STUD_SCHOOL_STATE_NAME = F("")
STUD_SCHOOL_NAME = F("stream__school__name")
STUD_STATUS = F("student__status")

STUD_STREAM_NAME = Concat(case_generator(CLASSES, "stream__base_class"), Value(" "), Coalesce(F("stream__name"), Value("")))
STUD_CORECT_FULL_NAME = Concat(Coalesce("first_name", Value("")), Value(" "), Coalesce("middle_name", Value("")), Value(" "), Coalesce("last_name", Value("")))
STUD_FULL_NAME = Concat(Coalesce("student__first_name", Value("")), Value(" "), Coalesce("student__middle_name", Value("")), Value(" "), Coalesce("student__last_name", Value("")))


STUDENTS_STATS_DEFINTIONS = {
    "class": {
        "value": F("stream__base_class"),
        "extra_fields": {
            "class_name": case_generator(CLASSES, "stream__base_class"),
        },
         "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "school": {
        "value": F("stream__school_id"),
        "extra_fields": {
            "school_name": STUD_SCHOOL_NAME,
            "village_name": STUDENT_SCHOOL_VILLAGE_NAME,
            "district_name": STUDENT_SCHOOL_DISTRICT_NAME,
            "state_name": STUDENT_SCHOOL_STATE_NAME,
            "region_name": STUDENT_SCHOOL_REGION_NAME,
        },
        "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "village": {
        "value": F("stream__school__village_id"),
        "extra_fields": {
            "village_name": STUDENT_SCHOOL_VILLAGE_NAME,
            "district_name": STUDENT_SCHOOL_DISTRICT_NAME,
            "state_name": STUDENT_SCHOOL_STATE_NAME,
            "region_name": STUDENT_SCHOOL_REGION_NAME,
        },
      "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "district": {
        "value": F("stream__school__village__district_id"),
        "extra_fields": {
            "state_name": STUDENT_SCHOOL_STATE_NAME,
            "region_name": STUDENT_SCHOOL_REGION_NAME,
            "district_name": STUDENT_SCHOOL_DISTRICT_NAME,
        },
       "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "partner":{
      "value":F("stream__school__partners__id"),
      "extra_fields":{
          "name":F("stream__school__partners__name"),
          "email":F("stream__school__partners__email"),
      },
      "enabled_filters": {
              **default_enabled_filter,
         }
    }, 
    "region": {
        "value": F("stream__school__village__district__region_id"),
        "extra_fields": {
            "state_name": STUDENT_SCHOOL_STATE_NAME,
            "region_name": STUDENT_SCHOOL_REGION_NAME,
            
        },
        "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "state": {
        "value": F("stream__school__village__district__region__state_id"),
        "extra_fields": {
            "state_name": STUDENT_SCHOOL_STATE_NAME,
        },
       "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "special-need": {
        "value": F("special_needs__id"),
        "extra_fields": {
            "special_need_name": F("special_needs__name"),
        },
       "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "gender": {
        "value": F("gender"),
        "extra_fields": {
            "gender_name": case_generator(STUDENT_GENDERS, "gender"),
        },
        "resp_fields": {
            # "count": Count("id"),
        },
        "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "age": {
        "value": RawSQL("date_part('year',age(date_of_birth))", ()),
        "extra_fields": {
            "age": F("value"),
        },
        "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "id": {
        "value": F("id"),
        "extra_fields": {
            "full_name": STUD_CORECT_FULL_NAME,
            "leaners_status": case_generator(STUDENT_STATUS, "status"),
            "leaners_gender": case_generator(STUDENT_GENDERS, "gender"),
            "class": STUD_STREAM_NAME,
            "admission_number": Coalesce(F("admission_no"), Value("XXX")),
            "school_name": STUD_SCHOOL_NAME,
            "enrolled_date": F("date_enrolled"),
            "leaners_birthday": F("date_of_birth"),
            "district_name": STUDENT_SCHOOL_DISTRICT_NAME,
            "region_name": STUDENT_SCHOOL_REGION_NAME,
            "village_name": STUDENT_SCHOOL_VILLAGE_NAME,
            "state_name": STUDENT_SCHOOL_STATE_NAME,
            **get_student_current_guardian(""),
        },
        "resp_fields": {
            "id",
            # "status",
            "date_of_birth",
            "date_enrolled",
            "distance_from_school",
            "live_with_parent",
        },
    },
    "student-status": {
        "value": F("status"),
        "extra_fields": {
            "status_name": case_generator(STUDENT_STATUS, "status"),
        },
    },
    "status": {
        "value": F("status"),
        "extra_fields": {
            "status_name": case_generator(STUDENT_STATUS, "status"),
        },
    },
    "dropout-reason": {"value": F("dropout_reason")},
    "knows-dob": {"value": F("knows_dob")},
    "month": {
        "value": Trunc("date_enrolled", "month", output_field=DateField()),
        "extra_fields": {
            "month": F("value"),
        },
    },
    "year": {
        "value": Trunc("date_enrolled", "year", output_field=DateField()),
        "extra_fields": {
            "year": F("value"),
        },
    },
    "day": {
        "value": TruncDate("date_enrolled", output_field=DateField()),
        "extra_fields": {
            "date": F("value"),
        },
    },
}

STUDENTS_STATS_DEFAULT_FIELDS = {
    "males": Count("id", filter=Q(gender="M")),
    "females": Count("id", filter=Q(gender="F")),
}


class DeleteReason(MyModel):
    name = models.CharField(unique=True, max_length=45)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


class StudentReactivation(MyModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="reacivations")
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="reactivations")
    reason = models.TextField(max_length=1500, null=True, blank=True)
    is_permament = models.BooleanField(default=False)

    def __str__(self):
        return "{} {}".format(self.student.first_name, self.description)

    class Meta:
        ordering = ("-id",)


class StudentDeleteReason(MyModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.ForeignKey(DeleteReason, on_delete=models.CASCADE)
    description = models.TextField(max_length=1500, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.student.first_name, self.reason.name)

    class Meta:
        ordering = ("id",)

    @staticmethod
    def get_role_filters():
        return {
            "A": None,
            "SCHA": "student__stream__school_id",
            "SCHT": "student__stream__school_id",
            "NGO": "student__stream__school_id",
            "CO": "student__stream__school__sub_county__county_id",
            "SCO": "student__stream__school__sub_county_id",
        }


REASON_DESCRIPTION = Case(
    When(
        reason__name="other",
        then=F("description"),
    ),
    default=F("reason__description"),
    output_field=CharField(),
)

STUD_SCHOOL_NAME = F("student__stream__school__name")
STUD_STATUS = case_generator(STUDENT_STATUS, "student__status")

STUD_FULL_NAME = Concat(Coalesce("student__first_name", Value("")), Value(" "), Coalesce("student__middle_name", Value("")), Value(" "), Coalesce("student__last_name", Value("")))

SCHOOL_REGION_NAME = F("student__village__district__region__name")
SCHOOL_DISTRICT_NAME = F("student__village__district__name")
SCHOOL_VILLAGE_NAME = F("student__village__name")
STUD_STATE_NAME = F("student__village__name")

STUD_SCHOOL_NAME = F("student__stream__school__name")
STUD_SCHOOL_VILLGE_NAME = F("student__stream__school__village__name")
STUD_SCHOOL_DISTRICT_NAME = F("student__stream__school__village__district__name")
STUD_SCHOOL_REGION_NAME = F("student__stream__school__village__district__region__name")
STUD_SCHOOL_STATE_NAME = F("student__stream__school__village__district__region__state__name")


STUD_STATUS = case_generator(STUDENT_STATUS, "student__status")


STUD_STREAM_NAME = Concat(case_generator(CLASSES, "student__stream__base_class"), Value(" "), Coalesce(F("student__stream__name"), Value("")))
STUD_FULL_NAME = Concat(Coalesce("student__first_name", Value("")), Value(" "), Coalesce("student__middle_name", Value("")), Value(" "), Coalesce("student__last_name", Value("")))
OTHER_REASON = Case(When(description__isnull=False, then=F("description")), default=Value(""))
STUDENT_DELETE_REASON_STATS_DEFINTIONS = {
    "id": {
        "value": F("id"),
        "extra_fields": {
            "date_added": TruncDay("created", output_field=DateField()),
            "full_name": STUD_FULL_NAME,
            "gender": case_generator(STUDENT_GENDERS, "student__gender"),
            "admission_number": Coalesce(F("student__admission_no"), Value("XXX")),
            "class": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "village_name": SCHOOL_VILLAGE_NAME,
            "district_name": SCHOOL_DISTRICT_NAME,
            "region_name": SCHOOL_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
            "date_of_birth": F("student__date_of_birth"),
            "date_enrolled": F("student__date_enrolled"),
            "student_status": STUD_STATUS,
            "reason_name": F("reason__description"),
            "admission_number": Coalesce(F("student__admission_no"), Value("XXX")),
            "other_reason": OTHER_REASON,  # F("description"),
            # "leaner_in_school": F("student__active"),
        },
        "resp_fields": {
            # "description",
        },
        "export_only_fields": {
            "special_needs_names": Coalesce(GroupConcat("student__special_needs__name", delimiter=", "), Value("None")),
        },
    },
     "partner":{
      "value":F("student__stream__school__partners__id"),
      "extra_fields":{
          "name":F("student__stream__school__partners__name"),
          "email":F("student__stream__school__partners__email"),
      }
    }, 
    "student": {
        "value": F("student_id"),
        "extra_fields": {
            "full_name": STUD_FULL_NAME,
            "gender": case_generator(STUDENT_GENDERS, "student__gender"),
            "admission_number": Coalesce(F("student__admission_no"), Value("XXX")),
            "class": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "village_name": SCHOOL_VILLAGE_NAME,
            "district_name": SCHOOL_DISTRICT_NAME,
            "region_name": SCHOOL_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
            "date_of_birth": F("student__date_of_birth"),
            "date_enrolled": F("student__date_enrolled"),
            "student_status": STUD_STATUS,
            "admission_number": Coalesce(F("student__admission_no"), Value("XXX")),
        },
        "resp_fields": {
            # "count": Count("id"),
        },
    },
    "class": {
        "value": F("student__stream__base_class"),
        "extra_fields": {
            "class_name": case_generator(CLASSES, "student__stream__base_class"),
        },
    },
    "stream": {
        "value": F("student__stream_id"),
        "extra_fields": {
            "class_name": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "village_name": STUD_SCHOOL_VILLGE_NAME,
            "district_name": STUD_SCHOOL_DISTRICT_NAME,
            "region_name": STUD_SCHOOL_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
    },
    "school": {
        "value": F("student__stream__school_id"),
        "extra_fields": {
            "school_name": STUD_SCHOOL_NAME,
            "village_name": STUD_SCHOOL_VILLGE_NAME,
            "district_name": STUD_SCHOOL_DISTRICT_NAME,
            "region_name": STUD_SCHOOL_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
    },
    "gender": {
        "value": F("student__gender"),
        "extra_fields": {
            "gender_name": case_generator(STUDENT_GENDERS, "student__gender"),
        },
        "resp_fields": {},
    },
    "reason": {
        "value": F("reason_id"),
        "extra_fields": {
            "reason_name": F("reason__description"),
        },
    },
    "reason-description": {
        "value": REASON_DESCRIPTION,
        "extra_fields": {},
        # "resp_fields": {},
    },
}


STUDENT_DELETE_REASON_STATS_DEFAULT_RESP_FIELDS = {
    "males": Count("id", filter=Q(student__gender="M")),
    "females": Count("id", filter=Q(student__gender="F")),
}


class AbsentReason(MyModel):
    name = models.CharField(unique=True, max_length=45)
    description = models.TextField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("id",)


class StudentAbsentReason(MyModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.ForeignKey(AbsentReason, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField(max_length=1500, null=True, blank=True)

    def __str__(self):
        return "{} {}".format(self.student.first_name, self.reason.name)

    class Meta:
        ordering = ("id",)
        unique_together = ("student", "date")

    @staticmethod
    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: "student__stream__school_id",
            MyUserRoles.SCHT.name: "student__stream__school_id",
            MyUserRoles.NGO.name: "student__stream__school_id",
            MyUserRoles.VLGA.name: "student__stream__school__village_id",
            MyUserRoles.DSTA.name: "student__stream__school__village__district_id",
            MyUserRoles.RGNA.name: "student__stream__school__village__district__region_id",
        }


IMPORT_STEPS = (
    ("Q", "Queued"),
    ("VH", "Validating Required Columns..."),
    ("PI", "Preparing..."),
    ("I", "Processing..."),
    ("F", "Failed"),
    ("D", "Done"),
)


class SchoolsStudentsImport(MyModel):
    name = models.CharField(max_length=45, null=True, blank=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    import_file = models.FileField(
        upload_to="imports",
    )
    step = models.CharField(choices=IMPORT_STEPS, default="Q", max_length=3, editable=False)
    errors_file = models.FileField(upload_to="imports", null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True, editable=False)
    end_time = models.DateTimeField(null=True, blank=True, editable=False)
    args = models.TextField(max_length=1000, null=True, blank=True, editable=False)
    rows_count = models.IntegerField(default=0, editable=False)
    imported_rows_count = models.IntegerField(default=0, editable=False)
    duplicates_count = models.IntegerField(default=0, editable=False)
    error_rows_count = models.IntegerField(default=0, editable=False)
    new_students_created = models.IntegerField(default=0, editable=False)
    should_import = models.BooleanField(default=True)

    errors = models.TextField(max_length=2000, default="")

    class Meta:
        ordering = ("-id",)

    @property
    def is_clean(self):
        if self.step != "D":
            return False
        if self.errors:
            return False
        return self.error_rows_count == 0

    @property
    def completed_steps(self):
        return []

    @property
    def duration(self):
        if self.start_time is None or self.end_time is None:
            return 0
        return self.end_time - self.start_time

    def prepare_import(self):
        self.imported_rows_count = 0
        self.rows_count = 0
        self.duplicates_count = 0
        self.step = "VH"
        self.errors = ""
        self.start_time = timezone.now()
        self.save()

    def start(self, rows_count):
        self.rows_count = rows_count
        self.step = "I"
        self.save()

    def append_count(self, rows_count):
        self.imported_rows_count += rows_count
        self.save()

    def finish(self, errors_file_path="", status="D", error_rows_count=0):
        if errors_file_path != "":
            self.errors_file.name = path.relpath(errors_file_path, MEDIA_ROOT)
        self.step = status
        self.end_time = timezone.now()
        self.error_rows_count = error_rows_count
        self.save()

    def set_errors(self, errors):
        self.errors = ""
        self.errors = errors
        self.step = "F"
        self.save()


class StudentSchoolTransfer(MyModel):
    from_school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="leaving_students")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    accept_stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    accept_class = models.CharField(choices=CLASSES, max_length=3)
    to_school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="joining_students")
    reason = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True, max_length=1000)
    accepted = models.BooleanField(default=False, editable=False)
    complete = models.BooleanField(default=False, editable=False)

    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: ["from_school_id", "to_school_id"],
            MyUserRoles.SCHT.name: ["from_school_id", "to_school_id"],
            MyUserRoles.NGO.name: ["from_school_id", "to_school_id"],
            MyUserRoles.VLGA.name: ["from_school__village_id", "to_school__village_id"],
            MyUserRoles.DSTA.name: ["from_school__village__district_id", "to_school__village__district_id"],
            MyUserRoles.RGNA.name: ["from_school__village__district__region_id", "to_school__village__district__region_id"],
        }


class StudentIntergrate(MyModel):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    from_stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="intergrating_students")
    to_stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="intergrated_students")
    description = models.TextField(null=True, blank=True, max_length=1000)
    can_reverse = models.BooleanField(default=True, editable=False)
    completed = models.BooleanField(default=False, editable=False)

    def get_role_filters():
        return {
            MyUserRoles.A.name: None,
            MyUserRoles.SCHA.name: "to_stream__school_id",
            MyUserRoles.SCHT.name: "to_stream__school_id",
            MyUserRoles.NGO.name: "to_stream__school_id",
            MyUserRoles.VLGA.name: "to_stream__school__village_id",
            MyUserRoles.DSTA.name: "to_stream__school__village__district_id",
            MyUserRoles.RGNA.name: "to_stream__school__village__district__region_id",
        }
