from rest_framework import serializers
from school.models import StudentIntergrate


class StudentIntergrateSerializer(serializers.ModelSerializer):
    from_stream_name = serializers.ReadOnlyField(source="from_stream.class_name")
    to_stream_name = serializers.ReadOnlyField(source="to_stream.class_name")
    student_name = serializers.ReadOnlyField(source="student.full_name")
    school_name = serializers.ReadOnlyField(source="from_stream.school.name")

    class Meta:
        model = StudentIntergrate
        fields = "__all__"

    def validate_to_stream(self, value):
        print(value)

        return value
