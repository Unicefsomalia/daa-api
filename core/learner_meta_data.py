from django.db.models.functions import Concat, Coalesce
from django.db.models import F, Case, When, CharField, Value

from school.models import CLASSES, STUDENT_GENDERS, STUDENT_STATUS

from core.common import get_single_student_field_name, get_student_current_guardian

from mylib.my_common import case_generator


def get_learner_stats_meta_data(student_field):
    data = {
        "full_name": Concat(
            Coalesce(get_single_student_field_name(student_field, "first_name"), Value("")),
            Value(" "),
            Coalesce(get_single_student_field_name(student_field, "middle_name"), Value("")),
            Value(" "),
            Coalesce(get_single_student_field_name(student_field, "last_name"), Value("")),
            Value(" "),
            Coalesce(get_single_student_field_name(student_field, "family_nick_name"), Value("")),
        ),
        "learner_gender": case_generator(STUDENT_GENDERS, get_single_student_field_name(student_field, "gender")),
        "class": Concat(
            case_generator(CLASSES, get_single_student_field_name(student_field, "stream__base_class")),
            Value(" "),
            Coalesce(get_single_student_field_name(student_field, "stream__name"), Value("")),
        ),
        "school_name": get_single_student_field_name(student_field, "stream__school__name"),
        "village_name": get_single_student_field_name(student_field, "stream__school__village__name"),
        "district_name": get_single_student_field_name(student_field, "stream__school__village__district__name"),
        "region_name": get_single_student_field_name(student_field, "stream__school__village__district__region__name"),
        "state_name": get_single_student_field_name(student_field, "stream__school__village__district__region__state__name"),
        "learner_status": case_generator(
            STUDENT_STATUS,
            get_single_student_field_name(student_field, "status"),
        ),
        "date_enrolled_": get_single_student_field_name(student_field, "date_enrolled"),
        "date_of_birth_": get_single_student_field_name(student_field, "date_of_birth"),
        "live_with_parent_": get_single_student_field_name(student_field, "live_with_parent"),
        "distance_from_school_": get_single_student_field_name(student_field, "distance_from_school"),
        "has_special_needs_": get_single_student_field_name(student_field, "has_special_needs"),
        "is_over_age_": get_single_student_field_name(student_field, "is_over_age"),
        "is_in_school": get_single_student_field_name(student_field, "active"),
        "learner_id": get_single_student_field_name(student_field, "id"),
        **get_student_current_guardian(student_field),
    }

    return data
