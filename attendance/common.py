import django

attendance_taken_signal = django.dispatch.Signal(providing_args=["date", "present", "absent", "stream"])


def get_stream_attendance_history_id(stream, date):
    return "{}{}".format(str(date).replace("-", ""), stream)
