from rest_framework import generics
from school.models import StudentIntergrate
from school.student_intergrates.serializers import StudentIntergrateSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination


class ListCreateStudentIntergratesAPIView(generics.ListCreateAPIView):
    serializer_class = StudentIntergrateSerializer
    queryset = StudentIntergrate.objects.all().select_related("student", "from_stream", "from_stream__school", "to_stream")
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)


class RetrieveUpdateDestroyStudentIntergrateAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = StudentIntergrateSerializer
    queryset = StudentIntergrate.objects.all().select_related("student", "from_stream", "from_stream__school", "to_stream")
    permission_classes = (IsAuthenticated,)
