
from rest_framework import  generics
from region.models import State
from region.states.serializers import StateSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination

class ListCreateStatesAPIView(generics.ListCreateAPIView):
    serializer_class = StateSerializer
    queryset = State.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

class RetrieveUpdateDestroyStateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StateSerializer
    queryset = State.objects.all()
    permission_classes = (IsAuthenticated,)
