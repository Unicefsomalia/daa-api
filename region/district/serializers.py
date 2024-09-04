from rest_framework import serializers

from region.models import District
from region.villages.serializers import VillageSerializer


class DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source="region.name", read_only=True)
    villages_details = VillageSerializer(source="villages", many=True, read_only=True)

    class Meta:
        model = District
        fields = "__all__"

        extra_kargs = {"unique_together": ("name", "region")}
