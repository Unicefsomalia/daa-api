from django.conf.urls import url

from attendance.student_absent_reason.views import ListCreateStudentAbsentReasonsAPIView, RetrieveUpdateDestroyStudentAbsentReasonAPIView
from school.absent_reason.views import ListStudenAbsentReasonDynamicStatisticsAPIView

urlpatterns = [
    url(r"^$", ListCreateStudentAbsentReasonsAPIView.as_view(), name="list_create_student_absent_reasons"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroyStudentAbsentReasonAPIView.as_view(), name="retrieve_update_destroy_student_absent_reason"),
    url(r"^stats/(?P<type>.+)/?$", ListStudenAbsentReasonDynamicStatisticsAPIView.as_view(), name="list_dynamic_student_absent_reasons_statistics"),
]
