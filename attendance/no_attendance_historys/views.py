from rest_framework import generics
from attendance.models import ATTENDANCE_TRACKING_STATS_DEFAULT_FIELDS, ATTENDANCE_TRACKING_STATS_DEFINTIONS, NoAttendanceHistory
from attendance.no_attendance_historys.serializers import GenerateAttendanceHistorySerializer, NoAttendanceHistorySerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination
from drf_autodocs.decorators import format_docstring

from stats.views import MyCustomDyamicStats

from core.common import DynamicStatsExtraFields


class ListCreateNoAttendanceHistorysAPIView(generics.ListCreateAPIView):
    serializer_class = NoAttendanceHistorySerializer
    queryset = NoAttendanceHistory.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return GenerateAttendanceHistorySerializer
        return self.serializer_class


class RetrieveUpdateDestroyNoAttendanceHistoryAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoAttendanceHistorySerializer
    queryset = NoAttendanceHistory.objects.all()
    permission_classes = (IsAuthenticated,)


NO_ATTENDANCE_HISTORY_STAT_TYES = [stat for stat in ATTENDANCE_TRACKING_STATS_DEFINTIONS]


@format_docstring({}, stat_types=", ".join(NO_ATTENDANCE_HISTORY_STAT_TYES))
class ListNoAttendanceHistoryDynamicStatisticsAPIView(MyCustomDyamicStats, generics.ListAPIView):
    """
    Group statistics by:
    `type` = {stat_types}
    """

    serializer_class = NoAttendanceHistorySerializer
    queryset = NoAttendanceHistory.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    stat_type = ""
    # filter_mixin=AttendanceFilter
    count_name = "total_missed_attendances"
    stats_definitions = ATTENDANCE_TRACKING_STATS_DEFINTIONS
    default_fields = ATTENDANCE_TRACKING_STATS_DEFAULT_FIELDS
    extra_filter_fields=[
        *DynamicStatsExtraFields
    ]
    
