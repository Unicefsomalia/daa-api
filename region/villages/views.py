from rest_framework import generics
from region.models import Village
from region.villages.serializers import VillageSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination


class ListCreateVillagesAPIView(generics.ListCreateAPIView):
    serializer_class = VillageSerializer
    queryset = Village.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)


class RetrieveUpdateDestroyVillageAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VillageSerializer
    queryset = Village.objects.all()
    permission_classes = (IsAuthenticated,)
