from django.db import models

# Create your models here.
from django.db.models import Count, Q, F, DateField, Value, FloatField, Min, Max, DecimalField, IntegerField
from django.db.models.expressions import RawSQL, Func
from django.db.models.functions import Trunc, TruncDate, Concat, Coalesce, Cast
from core.common import MyUserRoles, get_student_current_guardian

from mylib.my_common import MyModel, case_generator
from core.common import default_enabled_filter

from school.models import CLASSES, STUDENT_GENDERS, STUDENT_STATUS, Student, Stream, Teacher

ATTENDANCE_STATUS = ((1, "Present"), (0, "Absent"))


class Attendance(models.Model):
    id = models.CharField(primary_key=True, max_length=70)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.IntegerField(choices=ATTENDANCE_STATUS, default=0)  # assuming 1 is present 0 is absent
    cause_of_absence = models.CharField(max_length=200, null=True, blank=True)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, related_name="attendances")

    def __str__(self):
        return str(self.student)

    class Meta:
        ordering = ("id",)
        # unique_together=
        get_latest_by = "date"

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
            MyUserRoles.STA.name: "student__stream__school__village__district__region__state_id",
        }


STUD_REGION_NAME = F("village__district__region__name")
STUD_DISTRICT_NAME = F("village__district__name")
STUD_SHEHIYA_NAME = F("village__name")

STUD_SCHOOL_NAME = F("stream__school__name")
STUD_STATUS = case_generator(STUDENT_STATUS, "student__status")


STUD_STREAM_NAME = Concat(case_generator(CLASSES, "stream__base_class"), Value(" "), Coalesce(F("stream__name"), Value("")))
STUD_FULL_NAME = Concat(
    Coalesce("student__first_name", Value("")),
    Value(" "),
    Coalesce("student__middle_name", Value("")),
    Value(" "),
    Coalesce("student__last_name", Value("")),
    Value(" "),
    Coalesce("student__family_nick_name", Value("")),
)

ATTEND_REGION_NAME = F("stream__school__village__district__region__name")
ATTEND_DISTRICT_NAME = F("stream__school__village__district__name")
ATTEND_SHEHIYA_NAME = F("stream__school__village__name")
STUD_SCHOOL_STATE_NAME = F("stream__school__village__district__region__state__name")
ATT_MONTH = Trunc("date", "month", output_field=DateField())
ATT_WEEK = Trunc("date", "week", output_field=DateField())
TOTAL_DAYS = Count("date__date",distinct=True)
TOTAL_SCHOOLS = Count("stream__school_id",distinct=True)



# partner_name=

ATTENDANCE_ABOVE_SCHOOL_DEFAULTS={
     "schools_that_marked":TOTAL_SCHOOLS,
}


ATTENDANCE_ANY_RESP_DEFAULT={
     "total_days":TOTAL_DAYS,
}

ATTENDANCE_STATS_DEFINTIONS = {
    "id": {
        "value": F("id"),
        "extra_fields": {
            # "attendance_id":F("id"),
            "attendance": case_generator(ATTENDANCE_STATUS, "status"),
            "attendance_date": TruncDate("date", output_field=DateField()),
            "full_name": STUD_FULL_NAME,
            "gender": case_generator(STUDENT_GENDERS, "student__gender"),
            "admission_number": Coalesce(F("student__admission_no"), Value("XXX")),
            "date_enrolled": F("student__date_enrolled"),
            "date_of_birth": F("student__date_of_birth"),
            "class": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "student_status": STUD_STATUS,
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
        "resp_fields": {
            # "id": F("id"),
            # "status": F("status")
        },
    },
    "partner":{
      "value":F("stream__school__partners__id"),
      "extra_fields":{
          "name":F("stream__school__partners__name"),
          "email":F("stream__school__partners__email"),
      },
       "enabled_filters": {
              **default_enabled_filter,
         },
       "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    }, 
    "student": {
        "value": F("student_id"),
        "extra_fields": {
            "full_name": STUD_FULL_NAME,
            "gender": case_generator(STUDENT_GENDERS, "student__gender"),
            "class": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
            "student_status": STUD_STATUS,
            "date_enrolled": F("student__date_enrolled"),
            "date_of_birth": F("student__date_of_birth"),
            "student_id": F("student_id"),
            **get_student_current_guardian("student"),
        },
        "resp_fields": {
            "present_count": Count("id", filter=Q(status=1)),
            "absent_count": Count("id", filter=Q(status=0)),
             **ATTENDANCE_ANY_RESP_DEFAULT,
        },
        # "export_only_fields": {
        #     "special_needs_names": Coalesce(GroupConcat("student__special_needs__name", delimiter=", "), Value("None")),
        # },
    },
    "village": {
        "value": F("stream__school__village_id"),
        "extra_fields": {
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
        
    },
    "district": {
        "value": F("stream__school__village__district_id"),
        "extra_fields": {
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "region": {
        "value": F("stream__school__village__district__region_id"),
        "extra_fields": {
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "state": {
        "value": F("stream__school__village__district__region__state_id"),
        "extra_fields": {
            "state_name": STUD_SCHOOL_STATE_NAME,
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "class": {
        "value": F("stream__base_class"),
        "extra_fields": {
            "class_name": case_generator(CLASSES, "stream__base_class"),
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "stream": {
        "value": F("stream_id"),
        "grouping": "value",
        "extra_fields": {
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
            "school_name": F("stream__school__name"),
            "class_name": STUD_STREAM_NAME,
        },
        "resp_fields": {
            "present_count": Count("id", filter=Q(status=1)),
            "absent_count": Count("id", filter=Q(status=0)),
            "present_percentage": F("present_count") * 100.0 / (F("absent_count") + F("present_count")),
            "absent_percentage": F("absent_count") * 100.0 / (F("absent_count") + F("present_count")),
             **ATTENDANCE_ANY_RESP_DEFAULT,
        },
       "enabled_filters": {
              **default_enabled_filter,
         }
    },
    "school": {
        "value": F("stream__school_id"),
        "extra_fields": {
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "state_name": STUD_SCHOOL_STATE_NAME,
            "school_name": F("stream__school__name"),
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
       "extra_resp_fields":{
           "total_classes":Count("stream_id",distinct=True)
       }
    },
    "special-need": {
        "value": F("student__special_needs__id"),
        "extra_fields": {
            "special_need_name": F("student__special_needs__name"),
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
       "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "age": {
        "value": RawSQL(
            """
        date_part('year',age("school_student"."date_of_birth"))::int
        """,
            (),
        ),
        "extra_fields": {
            "age": F("value"),
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
       
    },
    "gender": {
        "value": F("student__gender"),
        "extra_fields": {
            "gender_name": case_generator(STUDENT_GENDERS, "value"),
        },
        "resp_fields": {
            "present_count": Count("id", filter=Q(status=1)),
            "absent_count": Count("id", filter=Q(status=0)),
            **ATTENDANCE_ANY_RESP_DEFAULT,
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
       "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "student-status": {
        "value": F("student__status"),
        "extra_fields": {
            "status_name": STUD_STATUS,
        },
       "enabled_filters": {
              **default_enabled_filter,
         },
       "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "dropout-reason": {"value": F("student__dropout_reason")},
    "knows-dob": {"value": F("student__knows_dob")},
    "month": {
        "value": ATT_MONTH,
        "extra_fields": {
            "month": F("value"),
        },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "week": {
        "value": ATT_WEEK,
        "extra_fields": {
            "week": F("value"),
        },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "year": {
        "value": Trunc("date", "year", output_field=DateField()),
        "extra_fields": {
            "year": F("value"),
        },
        "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
    "day": {
        "value": TruncDate("date", output_field=DateField()),
        "extra_fields": {
            "day": F("value"),
        },
       "extra_resp_fields":{
           **ATTENDANCE_ABOVE_SCHOOL_DEFAULTS
       }
    },
}

PRESENT_MALES = Count("id", filter=Q(status=1, student__gender="M"))
ABSENT_MALES = Count("id", filter=Q(status=0, student__gender="M"))
TOTAL_MALES = Count("id", filter=Q(student__gender="M"))

PRESENT_FEMALES = Count("id", filter=Q(status=1, student__gender="F"))
ABSENT_FEMALES = Count("id", filter=Q(status=0, student__gender="F"))
TOTAL_FEMALES = Count("id", filter=Q(student__gender="F"))


# =Cast(Count('name') / 2.0, FloatField()))
class Round(Func):
    function = "ROUND"
    arity = 2


RESP_FLOAT_FIELD = DecimalField(decimal_places=2)

ATTENDANCE_STATS_DEFAULT_FIELDS = {
   **ATTENDANCE_ANY_RESP_DEFAULT,
    "present_males": PRESENT_MALES,
    # "present_males_percentage": Round(PRESENT_MALES * Value(100.0) /  TOTAL_MALES ,1,output_field=FloatField()),
    "absent_males": ABSENT_MALES,
    # "absent_males_percentage":Round( ABSENT_MALES * Value(100.0) /  TOTAL_MALES ,1,output_field=FloatField()),
    "present_females": PRESENT_FEMALES,
    # "present_females_percentage":Round( PRESENT_FEMALES * Value(100.0)  /  TOTAL_FEMALES,1,output_field=FloatField()),
    "absent_females": ABSENT_FEMALES,
    # "absent_females_percentage":Round( ABSENT_FEMALES * Value(100.0) / TOTAL_FEMALES,1,output_field=FloatField()),
}

# total*1.0/SUM(total)
ATTENDANCE_STATS_DEFAULT_FIELDS_PERCENTAGE = {
    "present_males_percentage": Round(PRESENT_MALES * Value(100.0) / Count("id"), 1, output_field=FloatField()),
    "absent_males_percentage": Round(ABSENT_MALES * Value(100.0) / Count("id"), 1, output_field=FloatField()),
    "present_females_percentage": Round(PRESENT_FEMALES * Value(100.0) / Count("id"), 1, output_field=FloatField()),
    "absent_females_percentage": Round(ABSENT_FEMALES * Value(100.0) / Count("id"), 1, output_field=FloatField()),
}


class AttendanceTracking(MyModel):
    date = models.DateField()
    id = models.CharField(primary_key=True, blank=True, max_length=50)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)

    class Meta:
        abstract = True


ATTENDANCE_TRACKING_STATS_DEFINTIONS = {
    "id": {
        "value": F("id"),
        "extra_fields": {
            "class_name": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "missed_date": F("date"),
        },
        "resp_fields": {
            # "description",
        },
    },
    "stream": {
        "value": F("stream_id"),
        "extra_fields": {
            "class": STUD_STREAM_NAME,
            "school_name": STUD_SCHOOL_NAME,
            "village_name": ATTEND_SHEHIYA_NAME,
            "district_name": ATTEND_DISTRICT_NAME,
            "region_name": ATTEND_REGION_NAME,
            "region_name": ATTEND_REGION_NAME,
            "last_missed_date": Max("date"),
        },
    },
}
ATTENDANCE_TRACKING_STATS_DEFAULT_FIELDS = {
    # "days_count": Count("date", distinct=True),
}


class NoAttendanceHistory(AttendanceTracking):
    pass

    class Meta:
        ordering = ("-id",)


class AttendanceHistory(AttendanceTracking):
    present = models.IntegerField(default=0)
    absent = models.IntegerField(default=0)


class TeacherAttendance(MyModel):
    ATTENDANCE = ((1, "Present"), (0, "Absent"))
    id = models.CharField(primary_key=True, max_length=70)
    date = models.DateField()
    status = models.IntegerField(choices=ATTENDANCE, default=0)  # assuming 1 is present 0 is absent
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
