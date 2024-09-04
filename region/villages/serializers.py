from rest_framework import serializers
from region.models import Village


class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = "__all__"

        extra_kargs = {"unique_together": ("name", "district")}
