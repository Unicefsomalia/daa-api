import functools

from django.db.models import CharField
from django.utils import timezone
from rest_framework import serializers

from client.serializers import MyUserSerializer
from mylib.my_common import tuple_choices_to_map
from school.models import SchoolsStudentsImport, STUDENT_STATUS, STUDENT_GENDERS

from django.db.models.functions import Lower

CharField.register_lookup(Lower)


class SchoolsStudentsImportSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%a, %d %b %y %I:%M %p", read_only=True)
    modified = serializers.DateTimeField(format="%a, %d %b %y %I:%M %p", read_only=True)
    step_display = serializers.ReadOnlyField(source="get_step_display")
    user_details = MyUserSerializer(source="user", read_only=True)
    clean = serializers.ReadOnlyField()
    is_clean = serializers.ReadOnlyField()

    class Meta:
        model = SchoolsStudentsImport
        fields = "__all__"
        extra_kwargs = {"user": {"required": False}}


STUDENTS_ALL_STATUS = (*STUDENT_STATUS, ("NE", "Never Enrolled OOSC"), ("OOSC", "Previously Enrolled OOSC (Dropped out of school previously)"))

StudentstatusChoices = tuple_choices_to_map(STUDENTS_ALL_STATUS)

GENDER_CHOICES = (
    *STUDENT_GENDERS,
    ("M", "Boy"),
    ("M", "Boys"),
    ("F", "Girl"),
    ("F", "Girls"),
)
studentGenderChoices = tuple_choices_to_map(GENDER_CHOICES)

# print(StudentstatusChoices)
# print(studentGenderChoices)

DJANGO_DATE_INPUT_FORMATS = ["%Y-%m-%d %H:%M:%S %p", "%Y-%m-%d", "%Y", "%Y-%m-%d %H:%M:%S ", "%m/%d/%Y %H:%M:%S %p", "%m/%d/%Y", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S %p", "%d/%m/%Y %H:%M:%S","%d.%m.%Y"]


class StudentSchoolSerializer(serializers.Serializer):
    # School
    school_name = serializers.CharField()
    school_emis_code = serializers.CharField()
    school_email = serializers.CharField(required=False, allow_null=True)
    school_region = serializers.CharField()
    school_district = serializers.CharField()
    school_village = serializers.CharField()

    # Leaner
    first_name = serializers.CharField()
    middle_name = serializers.CharField(required=False, allow_null=True)
    last_name = serializers.CharField(required=False, allow_null=True)
    gender = serializers.CharField()
    stream = serializers.CharField()
    status = serializers.CharField(required=False, allow_null=True, default="PE")
    learner_region = serializers.CharField(required=False, allow_null=True)
    learner_district = serializers.CharField(required=False, allow_null=True)
    learner_village = serializers.CharField(required=False, allow_null=True)
    date_enrolled = serializers.DateTimeField(input_formats=DJANGO_DATE_INPUT_FORMATS, default=timezone.now)
    special_needs = serializers.CharField(required=False, allow_null=True)
    admission_number = serializers.CharField(required=False, allow_null=True)
    # upi = serializers.CharField(required=False, allow_null=True)
    date_of_birth = serializers.DateTimeField(input_formats=DJANGO_DATE_INPUT_FORMATS)
    distance_from_school = serializers.CharField(required=False, allow_null=True)

    # Guardian
    guardian_name = serializers.CharField(required=False, allow_null=True)
    guardian_region = serializers.CharField(required=False, allow_null=True)
    guardian_district = serializers.CharField(required=False, allow_null=True)
    guardian_village = serializers.CharField(required=False, allow_null=True)
    guardian_email = serializers.EmailField(required=False, allow_null=True)
    guardian_phone = serializers.CharField(required=False, allow_null=True)

    def validate_date_enrolled(self,value):
        print("validating date enrolled")
        print(type(value))
        print(value)
        return value
    
    def validate_stream(self,value):
        extractedints = list(filter(lambda a: a.isdigit(), value))
        if len(extractedints) < 1:
            raise serializers.ValidationError("No base class found. Options are ECD,1,2,3,4,5,6,7,8")
        return value
    
    def validate_gender(self, value):
        allowed_gender_values = ["m", "f", "female", "male"]
        if value.lower() not in allowed_gender_values:
            raise serializers.ValidationError("Wrong gender format")
        return "M" if value.lower() in ["m", "male"] else "F"

    def validate_distance_from_school(self, value):
        if value == None:
            return None

        strings = value.split(" ")
        extractedstring = list(filter(str.isdigit, map(lambda v: "".join(list(filter(str.isdigit, v))), strings)))
        extractedints = list(map(lambda x: int(x), extractedstring))
        total = functools.reduce(lambda a, b: a + b, extractedints)
        # print(extractedints,total)
        return "{}".format(int(total / len(extractedints)))

    def validate_status(self, value):
        if value == None:
            return "PE"

        status = StudentstatusChoices.get(value.lower().strip())
        if status:
            return status
        else:
            return "PE"


class SchoolImportSerializer(serializers.Serializer):
    school = serializers.CharField()
    school_nemis_code = serializers.CharField()
    county = serializers.CharField()
    subcounty = serializers.CharField()
