
from rest_framework import  generics
from region.models import County
from region.countys.serializers import CountySerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination

class ListCreateCountysAPIView(generics.ListCreateAPIView):
    serializer_class = CountySerializer
    queryset = County.objects.all().prefetch_related('sub_counties')
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

class RetrieveUpdateDestroyCountyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CountySerializer
    queryset = County.objects.all()
    permission_classes = (IsAuthenticated,)
