
from rest_framework import  generics
from region.models import SubCounty
from region.sub_countys.serializers import SubCountySerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination

class ListCreateSubCountysAPIView(generics.ListCreateAPIView):
    serializer_class = SubCountySerializer
    queryset = SubCounty.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

class RetrieveUpdateDestroySubCountyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubCountySerializer
    queryset = SubCounty.objects.all()
    permission_classes = (IsAuthenticated,)
