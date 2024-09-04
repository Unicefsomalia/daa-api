from email.policy import default
from django.utils import timezone
from rest_framework import serializers
from attendance.models import NoAttendanceHistory
from attendance.tasks import update_no_attendance_stream


class NoAttendanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoAttendanceHistory
        fields = "__all__"


class GenerateAttendanceHistorySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True, allow_null=False)
    end_date = serializers.DateField(required=True, allow_null=False)

    def create(self, validated_data):
        # print(validated_data)
        update_no_attendance_stream(start_date=validated_data["start_date"], end_date=validated_data["end_date"])
        # update_no_attendance_stream
        return validated_data
