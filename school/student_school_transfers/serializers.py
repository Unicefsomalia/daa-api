from secrets import choice
from rest_framework import serializers
from mylib.my_common import MyCustomException
from school.models import Stream, Student, StudentSchoolTransfer


class ReadStudentSchoolTransferSerializer(serializers.ModelSerializer):
    accept_class = serializers.ReadOnlyField(source="get_accept_class_display")
    from_school_name = serializers.ReadOnlyField(source="from_school.name")
    from_school_emis = serializers.ReadOnlyField(source="from_school.emis")
    to_school_name = serializers.ReadOnlyField(source="to_school.name")
    to_school_emis = serializers.ReadOnlyField(source="to_school.emis")
    accept_stream_name = serializers.ReadOnlyField(source="accept_stream.name")
    full_name = serializers.ReadOnlyField(source="student.full_name")
    gender = serializers.ReadOnlyField(source="student.gender")
    year = serializers.DateTimeField(read_only=True, source="created", format="%Y")
    accept_stream_name = serializers.ReadOnlyField(source="student.stream.class_name")

    class Meta:
        model = StudentSchoolTransfer
        fields = "__all__"


class StudentSchoolTransferSerializer(serializers.ModelSerializer):
    from_school_name = serializers.ReadOnlyField(source="from_school.name")
    from_school_emis = serializers.ReadOnlyField(source="from_school.emis")
    to_school_name = serializers.ReadOnlyField(source="to_school.name")
    to_school_emis = serializers.ReadOnlyField(source="to_school.emis")
    accept_stream_name = serializers.ReadOnlyField(source="accept_stream.name")
    full_name = serializers.ReadOnlyField(source="student.full_name")
    gender = serializers.ReadOnlyField(source="student.gender")
    year = serializers.DateTimeField(read_only=True, source="created", format="%Y")
    accept_stream_name = serializers.ReadOnlyField(source="student.stream.class_name")

    class Meta:
        model = StudentSchoolTransfer
        fields = "__all__"


class AcceptDenyStudentSchoolTransfer(serializers.Serializer):
    choices = ["deny", "accept"]
    accept_stream = serializers.IntegerField(required=True)

    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        bool_choice = self.get_bool_choice()
        self.fields.update({"accept_stream": serializers.IntegerField(required=bool_choice)})

    def validate(self, attrs):
        bool_choice = self.get_bool_choice()
        if bool_choice and attrs.get("accept_stream") == None:
            self.validate_accept_stream(None)
        return {**attrs, "accepted": bool_choice}

    def get_bool_choice(self):
        view = self.context.get("view")
        if view == None:
            return False
        choice = view.kwargs.get("school_choice")
        if choice not in self.choices:
            raise MyCustomException(f"Not a valid choice{self.choices}", 400)
        return True if choice.lower() == "accept" else False

    def validate_accept_stream(self, value):
        bool_choice = self.get_bool_choice()

        if bool_choice:
            if value == None or value == "":
                raise serializers.ValidationError({"accept_stream": "Stream is required if student is accepted."})
        if not Stream.objects.filter(id=value).exists():
            raise serializers.ValidationError("Stream does not exists. May have been delete.")

        stream = Stream.objects.filter(id=value).first()
        # if(stream.base)
        view = self.context.get("view")
        pk = view.kwargs.get("pk")
        inst = StudentSchoolTransfer.objects.filter(id=pk).first()
        if inst.accept_class != stream.base_class:
            # base_class_name = "Mbadala" if inst.accept_class == "0" else inst.accept_class
            raise serializers.ValidationError(f"You can only accept the leaner in class {base_class_name}")

        return value

    def update(self, instance, validated_data):
        view = self.context.get("view")
        for key, value in validated_data.items():
            if key == "accept_stream":
                setattr(instance, "accept_stream_id", value)
            else:
                setattr(instance, key, value)
        choice = view.kwargs.get("school_choice")
        instance.accepted = choice.lower() == "accept"
        if instance.accepted:
            ##Updaye student
            Student.objects.filter(id=instance.student_id).update(stream_id=instance.accept_stream_id, active=True)

        instance.complete = True
        instance.save()
        return validated_data
