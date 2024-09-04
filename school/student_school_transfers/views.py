from functools import partial
from rest_framework import generics
from school.models import Student, StudentSchoolTransfer
from school.student.serializers import StudentSerializer
from school.student_school_transfers.serializers import AcceptDenyStudentSchoolTransfer, ReadStudentSchoolTransferSerializer, StudentSchoolTransferSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import FilterBasedOnRole, MyDjangoFilterBackend, MyStandardPagination
from rest_framework.response import Response


class ListCreateStudentSchoolTransfersAPIView(FilterBasedOnRole, generics.ListCreateAPIView):
    serializer_class = StudentSchoolTransferSerializer
    queryset = StudentSchoolTransfer.objects.all().select_related(
        "from_school",
        "to_school",
        "accept_stream",
    )
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ReadStudentSchoolTransferSerializer
        return StudentSchoolTransferSerializer

    def perform_create(self, serializer):
        res = super(ListCreateStudentSchoolTransfersAPIView, self).perform_create(serializer)
        Student.objects.filter(id=serializer.data["student"]).update(active=False)
        # print(serializer.data["student"])


class RetrieveUpdateDestroyStudentSchoolTransferAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSchoolTransferSerializer
    queryset = StudentSchoolTransfer.objects.all().select_related(
        "from_school",
        "to_school",
        "accept_stream",
    )
    permission_classes = (IsAuthenticated,)


class AcceptDenyStudentSchoolTransferAPIView(generics.UpdateAPIView):
    serializer_class = AcceptDenyStudentSchoolTransfer
    queryset = StudentSchoolTransfer.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_context(self):
        res = super(AcceptDenyStudentSchoolTransferAPIView, self).get_serializer_context()
        return {**res, "view": self}

    def patch(self, request, *args, **kwargs):
        res = super().patch(request, *args, **kwargs)
        id = self.kwargs.get("pk")
        choice = self.kwargs.get("school_choice")
        if choice != "accept":
            return res
        transfer_student = StudentSchoolTransfer.objects.filter(id=id).first()
        res = StudentSerializer(transfer_student.student)
        return Response(res.data)
