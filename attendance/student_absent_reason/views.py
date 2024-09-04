from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from school.models import StudentAbsentReason
from attendance.student_absent_reason.serializers import StudentAbsentReasonSerializer
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination
from drf_autodocs.decorators import format_docstring
from school.models import STUDENT_DELETE_REASON_STATS_DEFINTIONS, STUDENT_DELETE_REASON_STATS_DEFAULT_RESP_FIELDS
from stats.views import MyCustomDyamicStats


class ListCreateStudentAbsentReasonsAPIView(generics.ListCreateAPIView):
    serializer_class = StudentAbsentReasonSerializer
    queryset = StudentAbsentReason.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    pagination_class = MyStandardPagination
    extra_filter_fields=[
            {
        "field_name": "student_stream__school__partners__id",
        "label": "Partner",
        "field_type": "number",
    },
    ]

    def perform_create(self, serializer):
        serializer.save()


class RetrieveUpdateDestroyStudentAbsentReasonAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentAbsentReasonSerializer
    queryset = StudentAbsentReason.objects.all()
