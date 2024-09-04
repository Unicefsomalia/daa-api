from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from translation.locale_translation_texts.serializers import LocaleTranslationTextSerializer
from translation.models import TranslationLocale


class TranslationLocaleSerializer(serializers.ModelSerializer):
    # text_translations_details = LocaleTranslationTextSerializer(many=True, required=False, source="text_translations", read_only=True)

    class Meta:
        model = TranslationLocale
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                message="Translation already exists",
                queryset=TranslationLocale.objects.all(),
                fields=["country_code", "language_code"],
            )
        ]
