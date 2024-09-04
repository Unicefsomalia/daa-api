from rest_framework import serializers

from client.models import MyUser
from client.serializers import MyUserSerializer


class ResetTeacherPasswordSerializer(serializers.Serializer):
    allowed_roles = ["SCHT", "SCHA", "RO"]
    username = serializers.CharField()
    new_password = serializers.CharField()

    def validate_username(self, value):
        if not MyUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("User does not exist.")
        user = MyUser.objects.get(username=value)
        if user.role not in self.allowed_roles:
            raise serializers.ValidationError("Admin assisted password reset is for teacher accounts only.")
        return value


class RoleBasedCharField(serializers.CharField):
    @staticmethod
    def _validate_phone_number(value):
        digits = re.sub(r"\D", "", value)
        if len(digits) != 11:
            raise serializers.ValidationError("Phone number must contain 11 digits.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(args)
        # print(kwargs)
        # print(self.initial)
        # self.validators.append(PhoneNumberField._validate_phone_number)

    def to_internal_value(self, data):
        print(data)
        data = super().to_internal_value(data)
        return data


class SystemUserSerializer(MyUserSerializer):
    def __init__(self, *args, **kwargs):
        super(SystemUserSerializer, self).__init__(**kwargs)
        self.fields.update({"ids": serializers.ListField(child=serializers.CharField(required=True), required=True)})

    def create(self, validated_data):
        print("Create system users")
        # super(SystemUsersCountyTests ,self).setUp()
        ids = validated_data.pop("ids")
        self.fields.pop("ids")

        if ids != None:
            args = ""
            if type(ids) == list:
                args = ",".join(ids)
            else:
                args = ids
            # print(type(id), args)
            validated_data["filter_args"] = args
        # print(validated_data)
        return super(SystemUserSerializer, self).create(validated_data)
