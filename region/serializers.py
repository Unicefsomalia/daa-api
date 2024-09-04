from ast import Try
from email.policy import default
from rest_framework import serializers
from region.district.serializers import DistrictSerializer

from region.models import Region


class RegionSerializer(serializers.ModelSerializer):
    districts_details = DistrictSerializer(many=True, source="districts", read_only=True)

    class Meta:
        model = Region
        fields = "__all__"

        extra_kargs = {"unique_together": ("name", "state")}
