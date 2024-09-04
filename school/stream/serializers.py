from email.policy import default
from rest_framework import serializers

from school.models import Stream, Student, School
from school.student.serializers import StudentSerializer


class StreamSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)
    class_name = serializers.ReadOnlyField()
    full_class_name = serializers.ReadOnlyField()
    name = serializers.CharField(default="", required=False, allow_blank=True)

    class Meta:
        model = Stream
        fields = "__all__"
        extra_kwargs = {"unique_together": ("school", "name")}

    def validate_name(self, value):
        school = self.initial_data.get("school", None)
        base_class = self.initial_data.get("base_class", None)
        instance = self.context.get("instance")
        queryset = Stream.objects.all()
        if instance != None:
            queryset = queryset.exclude(id=instance.id)

        if queryset.filter(name__iexact=value, school=school, base_class=base_class):
            raise serializers.ValidationError("Stream already exists.")
        return value


class StudentsStreamSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    class_name = serializers.ReadOnlyField()
    
    # class_name = serializers.SerializerMethodField()
    class Meta:
        model = Stream
        fields = "__all__"

    def get_students(self, obj):
        # print("getting students..")
        queryset = Student.objects.filter(stream_id=obj.id, active=True).select_related("stream")
        ser = StudentSerializer(queryset, many=True)
        return ser.data
