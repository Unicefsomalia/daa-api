from rest_framework import serializers
from translation.models import LocaleTranslationText
from rest_framework.validators import UniqueTogetherValidator


class LocaleTranslationTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocaleTranslationText
        fields = "__all__"

    validators = [
        UniqueTogetherValidator(
            message="Translation text already exists",
            queryset=LocaleTranslationText.objects.all(),
            fields=["text", "locale"],
        )
    ]
