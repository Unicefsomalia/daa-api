import datetime
from email.policy import default
from urllib import request

from django.utils import timezone
from rest_framework import serializers, fields
from rest_framework.serializers import ModelSerializer
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin
from mylib.my_common import MyCustomException

from school.models import Stream, Student, SPECIAL_NEEDS, StudentDeleteReason, StudentAbsentReason, StudentReactivation
from school.special_needs.serializers import SpecialNeedSerializer


class ReactivateLeanerSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)
    stream = serializers.IntegerField(required=True)
    reason = serializers.CharField(required=True, allow_blank=False)

    def validate_stream(self, value):
        print("Validating stream")
        if not Stream.objects.filter(id=value).exists():
            raise serializers.ValidationError("Stream does not exists. May have been delete.")
        return value

    def validate(self, attrs):
        view = self.context.get("view")
        id = view.kwargs.get("pk")
        if attrs.get("stream", None) == None:
            raise serializers.ValidationError({"stream": "This field is required."})

        if attrs.get("reason", None) == None:
            raise serializers.ValidationError({"reason": "This field is required."})
        if not Student.objects.filter(id=id).exists():
            raise MyCustomException("Learner not found")
        student = Student.objects.filter(id=id).first()
        if student.active:
            raise MyCustomException("Learner already activate.")
        return attrs

    def update(self, instance, validated_data):
        view = self.context.get("view")
        id = view.kwargs.get("pk")
        student = Student.objects.filter(id=id).first()
        student.active = True
        student.stream_id = validated_data.get("stream")
        student.save()
        ## TODO: Delete anu transfer request

        StudentReactivation.objects.create(
            reason=validated_data.get("reason"),
            student_id=id,
            stream_id=validated_data.get("stream"),
        )
        validated_data["detail"] = "Student activated successfully."
        return validated_data


class StudentSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="stream.school.name", read_only=True)
    stream_name = serializers.CharField(source="stream.name", read_only=True)
    class_name = serializers.CharField(source="stream.class_name", read_only=True)
    base_class = serializers.CharField(source="stream.base_class", read_only=True)
    full_name = serializers.ReadOnlyField()
    student_id = serializers.ReadOnlyField()
    date_enrolled = serializers.DateField(default=datetime.date.today)
    special_needs_details = SpecialNeedSerializer(many=True, source="special_needs", read_only=True, default=[])

    state = serializers.ReadOnlyField(source="village.district.region.state_id", default=None)
    region = serializers.ReadOnlyField(source="village.district.region_id", default=None)
    district = serializers.ReadOnlyField(source="village.district_id", default=None)

    age = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField(source="get_status_display")
    gender_display = serializers.ReadOnlyField(source="get_gender_display")
    gender_display = serializers.ReadOnlyField(source="get_gender_display")
    pre_primary_attendend_display = serializers.ReadOnlyField(source="get_pre_primary_attendend_display")
    

    state_name = serializers.ReadOnlyField(source="village.district.region.state.name", default="N/A")
    region_name = serializers.ReadOnlyField(source="village.district.region.name", default="N/A")
    district_name = serializers.ReadOnlyField(source="village.district.name", default="N/A")
    village_name = serializers.ReadOnlyField(source="village.name", default="N/A")

    current_guardian_name = serializers.ReadOnlyField()
    current_guardian_phone = serializers.ReadOnlyField()
    current_guardian_relationship = serializers.ReadOnlyField()

    father_status_display = serializers.ReadOnlyField(source="get_father_status_display")
    mother_status_display = serializers.ReadOnlyField(source="get_mother_status_display")

    # Guardian
    guardian_region_name = serializers.ReadOnlyField(source="guardian_village.district.region.name", default="N/A")
    guardian_district_name = serializers.ReadOnlyField(source="guardian_village.district.name", default="N/A")
    guardian_village_name = serializers.ReadOnlyField(source="guardian_village.name", default="N/A")
    guardian_status_display = serializers.ReadOnlyField(source="get_guardian_status_display")
    guardian_region = serializers.ReadOnlyField(source="guardian_village.district.region_id", default=None)
    guardian_district = serializers.ReadOnlyField(source="guardian_village.district_id", default=None)

    class Meta:
        model = Student
        fields = "__all__"


class SimpleStudentAbsentSerializer(serializers.ModelSerializer):
    reason_name = serializers.CharField(source="reason.name")
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    student_id = serializers.ReadOnlyField()
    special_needs_details = SpecialNeedSerializer(many=True, source="special_needs", read_only=True)

    class Meta:
        model = StudentAbsentReason
        fields = ("reason", "reason_name", "description", "id", "age", "full_name", "student_id", "special_needs_details")


class AbsentStudentSerializer(StudentSerializer):
    reason_absent = serializers.SerializerMethodField()

    def get_reason_absent(self, obj):
        date = self.context.get("request").query_params.get("date")
        if date:
            re = list(StudentAbsentReason.objects.filter(date=date, student_id=obj.id))
            if len(re) > 0:
                return SimpleStudentAbsentSerializer(re[0]).data
        return None


class SimpleStudentSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = ("first_name", "last_name", "id", "age")


class DeleteStudentSerializer(serializers.ModelSerializer):
    dropout_reason = serializers.CharField(source="reason.name", read_only=True)
    first_name = serializers.CharField(source="student.first_name", read_only=True)
    stream_name = serializers.CharField(source="student.stream.name", read_only=True)
    base_class = serializers.CharField(source="student.stream.base_class", read_only=True)
    school = serializers.CharField(source="student.stream.school", read_only=True)
    school_emis_code = serializers.CharField(source="student.stream.school.emis_code", read_only=True)
    school_name = serializers.CharField(source="student.stream.school.name", read_only=True)
    middle_name = serializers.CharField(source="student.middle_name", read_only=True)
    last_name = serializers.CharField(source="student.last_name", read_only=True)
    admission_no = serializers.CharField(source="student.admission_no", read_only=True)
    reason_description = serializers.CharField(source="reason.description", read_only=True)

    class Meta:
        model = StudentDeleteReason
        fields = "__all__"


class BulkStudentSerializer(BulkSerializerMixin, ModelSerializer):
    school_name = serializers.CharField(source="stream.school.name", read_only=True)
    stream_name = serializers.CharField(source="stream.name", read_only=True)
    class_name = serializers.CharField(source="stream.class_name", read_only=True)
    base_class = serializers.CharField(source="stream.base_class", read_only=True)
    full_name = serializers.ReadOnlyField()
    student_id = serializers.ReadOnlyField()
    date_enrolled = serializers.DateField(default=datetime.date.today)
    special_needs_details = SpecialNeedSerializer(many=True, source="special_needs", read_only=True)
    region = serializers.ReadOnlyField(source="village.district.region_id")
    district = serializers.ReadOnlyField(source="village.district_id")
    # village = serializers.ReadOnlyField(source="village_id")

    current_guardian_name = serializers.ReadOnlyField()
    current_guardian_phone = serializers.ReadOnlyField()

    age = serializers.ReadOnlyField()
    status_display = serializers.ReadOnlyField(source="get_status_display")
    gender_display = serializers.ReadOnlyField(source="get_gender_display")

    father_status_display = serializers.ReadOnlyField(source="get_father_status_display")
    mother_status_display = serializers.ReadOnlyField(source="get_mother_status_display")

    region_name = serializers.ReadOnlyField(source="village.district.region.name", default="N/A")
    district_name = serializers.ReadOnlyField(source="village.district.name", default="N/A")
    village_name = serializers.ReadOnlyField(source="village.name", default="N/A")

    # Guardian
    guardian_region_name = serializers.ReadOnlyField(source="guardian_village.district.region.name", default="N/A")
    guardian_district_name = serializers.ReadOnlyField(source="guardian_village.district.name", default="N/A")
    guardian_village_name = serializers.ReadOnlyField(source="guardian_village.name", default="N/A")
    guardian_status_display = serializers.ReadOnlyField(source="get_guardian_status_display")
    guardian_region = serializers.ReadOnlyField(source="guardian_village.district.region_id")
    guardian_district = serializers.ReadOnlyField(source="guardian_village.district_id")

    class Meta(object):
        model = Student
        fields = "__all__"
        # only necessary in DRF3
        list_serializer_class = BulkListSerializer


class EnrollmentSerializer(serializers.Serializer):
    males = serializers.IntegerField()
    females = serializers.IntegerField()
    dropout_males = serializers.IntegerField()
    dropout_females = serializers.IntegerField()
    value = serializers.CharField()
    total = serializers.SerializerMethodField()
    active_total = serializers.SerializerMethodField()
    dropout_total = serializers.SerializerMethodField()

    def get_total(self, obj):
        return obj["males"] + obj["females"] + obj["dropout_males"] + obj["dropout_females"]

    def get_active_total(self, obj):
        return obj["males"] + obj["females"]

    def get_dropout_total(self, obj):
        return obj["dropout_males"] + obj["dropout_females"]

    def to_representation(self, instance):
        # data = super(EnrollmentSerializer, self).to_representation(instance)
        return instance
