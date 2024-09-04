from django_filters.rest_framework import FilterSet, DjangoFilterBackend
import school.models as school_models
import django_filters
from django.db import models

# partner = django_filters.NumberFilter(field_name="stream__school__partners__id", label="Partner Id")
BASE_STUDENT_REASON_FILTERS = [
    {
        "field_name": "student__stream__school_id",
        "label": "School",
        "field_type": "number",
    },
    {
        "field_name": "student_stream__school__partners__id",
        "label": "Partner",
        "field_type": "number",
    },
    {
        "field_name": "student__stream__base_class",
        "label": "Base Class",
        "field_type": "char",
    },
    {
        "field_name": "student__stream__school__village_id",
        "label": "School Village",
        "field_type": "number",
    },
    {
        "field_name": "student__stream__school__village__district_id",
        "label": "School District",
        "field_type": "number",
    },
    {
        "field_name": "student__stream__school__village__district__region_id",
        "label": "School Region",
        "field_type": "number",
    },
    {
        "field_name": "student__stream__school__village__district__region__state_id",
        "label": "School State",
        "field_type": "number",
    },
    {
        "field_name": "created__date",
        "lookup_expr": "gte",
        "label": "Start Recorded Date",
        "field_type": "date",
    },
    {
        "field_name": "created__date",
        "lookup_expr": "lte",
        "label": "End Recorded Date",
        "field_type": "date",
    },
]

class SchoolFilter(FilterSet):
    has_partner=django_filters.BooleanFilter(method="filter_has_partner",label="Has Partner")
    partner_name = django_filters.NumberFilter(field_name="partners__name",lookup_expr="icontains", label="Stream Id")
    
    class Meta:
        model = school_models.School
        fields = "__all__"
    
    def filter_has_partner(self,queryset,name,value):
        print("Filter Value ",value)
        return queryset.annotate(
            has_authors=models.Exists(school_models.School.partners.through.objects.filter(school_id=models.OuterRef('pk')))
        ).filter(has_authors=value)
        
