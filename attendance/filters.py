import django_filters
from django_filters.rest_framework import FilterSet, DjangoFilterBackend

from attendance.models import Attendance
from mylib.my_common import str2bool
from school.models import STUDENT_STATUS
import school.models as school_models
from django.db import models

class AttendanceFilter(FilterSet):
    GENDERS = (
        ("M", "Male"),
        ("F", "Female"),
    )
    base_class = django_filters.CharFilter(field_name="stream__base_class", label="Class")
    date = django_filters.DateFilter(field_name="date__date", label="date")
    start_date = django_filters.DateFilter(field_name="date", lookup_expr="gte", label="Start Date")
    end_date = django_filters.DateFilter(field_name="date", lookup_expr=("lte"), label="End Date")
    gender = django_filters.ChoiceFilter(field_name="student__gender", label="gender", choices=GENDERS)
    school = django_filters.NumberFilter(field_name="stream__school", label="School")
    school_emis_code = django_filters.NumberFilter(field_name="stream__school__emis_code", label="School Emis Code", lookup_expr="icontains")
    leaner_status = django_filters.ChoiceFilter(field_name="student__status", label="Leaner Status", choices=STUDENT_STATUS)

    school_district = django_filters.NumberFilter(field_name="stream__school__village__district_id", label="School District Id")
    school_region = django_filters.NumberFilter(field_name="stream__school__village__district__region_id", label="School Region Id")
    school_state = django_filters.NumberFilter(field_name="stream__school__village__district__region__state_id", label="School State Id")
    school_village = django_filters.NumberFilter(field_name="stream__school__village_id", label="School Village Id")

    year = django_filters.NumberFilter(field_name="date__year", label="Year")
    month = django_filters.NumberFilter(field_name="date__month", label="Month")
    special_needs = django_filters.NumberFilter(field_name="student__special_needs", label="Special Needs Id")
    partner = django_filters.NumberFilter(field_name="stream__school__partners__id", label="Partner Id")
    has_partner=django_filters.BooleanFilter(method="filter_has_partner",label="Has Partner")

    class Meta:
        model = Attendance
        fields = "__all__"

    def filter_partner(self, queryset, name, value):
        return queryset.filter(stream__school__partners__id=value)

    def filter_is_oosc(self, queryset, name, value):
        return queryset.filter(student__is_oosc=str2bool(value))
    
    def filter_has_partner(self,queryset,name,value):
        return queryset.annotate(
            has_authors=models.Exists(school_models.School.partners.through.objects.filter(school_id=models.OuterRef('stream__school_id')))
        ).filter(has_authors=value)
        

    def filter_partner_admin(self, queryset, name, value):
        return queryset.filter(stream__school__partners__partner_admins__id=value)
