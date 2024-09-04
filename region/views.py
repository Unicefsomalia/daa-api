from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination
from mylib.mygenerics import MyListAPIView
from region.district.serializers import DistrictSerializer
from region.models import Region, District
from region.serializers import RegionSerializer


class ListCreateRegionsAPIView(generics.ListCreateAPIView):
    serializer_class = RegionSerializer
    queryset = Region.objects.all().prefetch_related("districts", "districts__villages")
    filter_backends = (MyDjangoFilterBackend,)
    pagination_class = MyStandardPagination


class RetrieveUpdateDestroyRegionAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RegionSerializer
    queryset = Region.objects.all().prefetch_related("districts", "districts__villages")
    permission_classes = (IsAuthenticated,)


class ListRegionDistricts(MyListAPIView):
    foreign_key_field = "region"
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    pagination_class = MyStandardPagination
