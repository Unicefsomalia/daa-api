from django.conf.urls import url
from attendance.no_attendance_historys.views import ListCreateNoAttendanceHistorysAPIView, ListNoAttendanceHistoryDynamicStatisticsAPIView, RetrieveUpdateDestroyNoAttendanceHistoryAPIView

urlpatterns = [
    url(r"^$", ListCreateNoAttendanceHistorysAPIView.as_view(), name="list_create_no_attendance_historys"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroyNoAttendanceHistoryAPIView.as_view(), name="retrieve_update_destroy_no_attendance_history"),
    url(r"^stats/(?P<type>.+)/?$", ListNoAttendanceHistoryDynamicStatisticsAPIView.as_view(), name="list_dynamic_student_no_attendance_statistics"),
]
