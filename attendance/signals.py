from django.dispatch import receiver

from attendance.models import AttendanceHistory, NoAttendanceHistory

from attendance.common import attendance_taken_signal, get_stream_attendance_history_id


@receiver(attendance_taken_signal)
def receive_attendance_taken(date, present, absent, stream, **kwargs):
    # print("REceived the signal")
    # print(date, present, absent, stream)
    try:
        id = get_stream_attendance_history_id(stream=stream, date=date)
        # print(id)
        at = AttendanceHistory.objects.get_or_create(id=id, present=present, stream_id=stream, absent=absent, date=date)
        # print(at)
        # Delete any no attendance history
        NoAttendanceHistory.objects.filter(id=id).delete()
    except Exception as e:
        print(e)
        pass
