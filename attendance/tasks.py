from datetime import timedelta
import datetime
from attendance.models import Attendance, NoAttendanceHistory
from school.models import Stream
from attendance.common import get_stream_attendance_history_id


def generate_dates(start_date, end_date):
    result = []
    current_date = start_date
    while current_date <= end_date:
        result.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return result


# start = datetime.strptime("2022-01-01", "%Y-%m-%d")
# end = datetime.strptime("2022-12-31", "%Y-%m-%d")


def update_no_attendance_stream(start_date, end_date, user=None):
    # print("Hello there")
    date_range = generate_dates(start_date=start_date, end_date=end_date)
    # print(date_range)
    streams_iterator = Stream.objects.all().iterator(chunk_size=6000)
    for stream in streams_iterator:
        print(stream)
        stream_attendances = [
            {
                "id": get_stream_attendance_history_id(stream.id, date),
                "date": date,
                "stream_id": stream.id,
            }
            for date in date_range
        ]
        date_range_ids = [stream_attendance["id"] for stream_attendance in stream_attendances]
        # print(date_range_ids)
        valid_ids = list(Attendance.objects.filter(id__in=date_range_ids).values_list("id", flat=True))
        # print(valid_ids)
        missing_attendances = list(filter(lambda att: att["id"] not in valid_ids, stream_attendances))
        # print(missing_attendances)

        id = NoAttendanceHistory.objects.filter(date__gte=start_date, date__lte=end_date, stream_id=stream.id).delete()

        missing_attendances_id = [att["id"] for att in missing_attendances]
        not_updated_missing_attendances = list(NoAttendanceHistory.objects.filter(id__in=missing_attendances_id).values_list("id", flat=True))

        to_create_no_attendances_historys = list(filter(lambda att: att["id"] not in not_updated_missing_attendances, missing_attendances))

        bulk_missing_attendances = [NoAttendanceHistory(**missing_attendance) for missing_attendance in to_create_no_attendances_historys]
        res = NoAttendanceHistory.objects.bulk_create(bulk_missing_attendances)
        # print(res)

        # NoAttendanceHistory
