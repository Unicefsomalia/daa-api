
from rest_framework import serializers
from region.models import State
from region.serializers import RegionSerializer
class StateSerializer(serializers.ModelSerializer):
    regions_details = RegionSerializer(many=True, source="regions", read_only=True)

    class Meta:
        model=State
        fields=("__all__")
