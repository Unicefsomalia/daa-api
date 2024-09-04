
from rest_framework import serializers
from translation.models import TranslationText
class TranslationTextSerializer(serializers.ModelSerializer):
    class Meta:
        model=TranslationText
        fields=("__all__")
