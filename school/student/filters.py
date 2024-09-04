import django_filters
from django.db.models import Q
from django.db import models
from school.models import Student
from django_filters.rest_framework import FilterSet
import school.models as school_models


class EnrollmentFilter(FilterSet):
    base_class = django_filters.NumberFilter(field_name="stream__base_class", label="Stream Id")
    school = django_filters.NumberFilter(field_name="stream__school_id", label="School Id")

    school_district = django_filters.NumberFilter(field_name="stream__school__village__district_id", label="School District Id")
    school_region = django_filters.NumberFilter(field_name="stream__school__village__district__region_id", label="School Region Id")
    school_state = django_filters.NumberFilter(field_name="stream__school__village__district__region__state_id", label="School State Id")
    school_village = django_filters.NumberFilter(field_name="stream__school__village_id", label="School Village Id")

    school_emis_code = django_filters.NumberFilter(field_name="stream__school__emis_code", label="School emis code")
    start_date = django_filters.DateFilter(field_name="date_enrolled", lookup_expr=("gte"))
    end_date = django_filters.DateFilter(field_name="date_enrolled", lookup_expr=("lte"))
    year = django_filters.NumberFilter(field_name="date_enrolled", lookup_expr=("year"))
    name = django_filters.CharFilter(method="filter_students_by_names", label="Any Student Name")
    partner = django_filters.NumberFilter(field_name="stream__school__partners__id", label="Partner Id")
    has_partner=django_filters.BooleanFilter(method="filter_has_partner",label="Has Partner")
    
    class Meta:
        model = Student
        exclude = ("moe_extra_info",)
        fields = "__all__"

    # def filter_partner(self, queryset, name, value):
    #     return queryset.filter(stream__school__partners__id=value)

    def filter_has_partner(self,queryset,name,value):
        return queryset.annotate(
            has_authors=models.Exists(school_models.School.partners.through.objects.filter(school_id=models.OuterRef('stream__school_id')))
        ).filter(has_authors=value)
        
        
    def filter_students_by_names(self, queryset, name, value):
        names = value.split(" ")
        if len(names) > 2:
            return queryset.filter(Q(first_name__icontains=names[0]), Q(middle_name__icontains=names[1]), Q(last_name__icontains=names[2]))
        elif len(names) == 2:
            return queryset.filter(Q(first_name__icontains=names[0]), (Q(last_name__icontains=names[1]) | Q(middle_name__icontains=names[1])))

        return queryset.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(middle_name__icontains=value))
