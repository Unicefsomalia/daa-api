import enum
from django.conf import settings


MyUser = getattr(settings, "AUTH_USER_MODEL", "auth.User")
from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.models import F, Case, When, CharField, Value
from django.db.models.functions import Concat, Coalesce

default_enabled_filter={
    
            "value__isnull": False,
        
}


DynamicStatsExtraFields=[
    # {
    #     "field_name": "value",
    #     "label": "Include Null",
    #     "field_type": "bool",
    #     "lookup_expr":"isnull"
    #     }
]
class MyUserRoles(enum.Enum):
    A = "Admin"
    SCHA = "School Admin"
    SCHT = "School Teacher"
    VLGA = "Village Admin"
    DSTA = "District Admin"
    RGNA = "Region Admin"
    NGO = "Partner Admin"
    STA = "State Admin"

"""
from mylib.my_common import get_redirect_url

mylib.my_common.MyStandardPagination
get_redirect_url()
"""

FORM_STAGES = (
    ("R", "Reception"),
    ("T", "Triage"),
    ("C", "Cashier"),
    ("D", "Doctor"),
    ("CL", "Cashier Lab"),
    ("L", "Lab"),
    ("DFL", "Doctor From Lab"),
    ("CP", "Cashier Pharmacy"),
    ("P", "Pharmacy"),
)


def get_single_student_field_name(student_field, field_name):
    parts = []
    if student_field != "":
        parts.append(student_field)
    parts.append(field_name)
    field_name = "__".join(parts)
    # print(field_name)
    return field_name


def get_student_current_guardian(student_field):
    def get_field(name):
        return get_single_student_field_name(student_field=student_field, field_name=name)

    # live_with_guardin_name=
    # print(f"Field is {student_field}")
    res = {
        "current_guardian_name": Case(
            When(**{f"{get_field('live_with_parent')}": False, "then": F(get_field(("guardian_name")))}),
            When(**{f"{get_field('father_name')}__isnull": False, "then": F(get_field("father_name"))}),
            When(**{f"{get_field('mother_name')}__isnull": False, "then": F(get_field("mother_name"))}),
            default=F(get_field("guardian_name")),
            output_field=CharField(),
        ),
        "current_guardian_phone": Case(
            When(**{f"{get_field('live_with_parent')}": False, "then": F(get_field("guardian_phone"))}),
            When(**{f"{get_field('father_phone')}__isnull": False, "then": F(get_field("father_phone"))}),
            When(**{f"{get_field('mother_phone')}__isnull": False, "then": F(get_field("mother_phone"))}),
            default=F(get_field("guardian_phone")),
            output_field=CharField(),
        ),
        "current_guardian_relationship": Case(
            When(**{f"{get_field('live_with_parent')}": False, "then": F(get_field("guardian_relationship"))}),
            When(**{f"{get_field('father_phone')}__isnull": False, "then": Value("Father")}),
            When(**{f"{get_field('mother_phone')}__isnull": False, "then": Value("Mother")}),
            default=F(get_field("guardian_relationship")),
            output_field=CharField(),
        ),
    }
    # print(res)
    return res
