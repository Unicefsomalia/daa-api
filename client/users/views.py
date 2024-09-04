from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from client.filters import UsersFilter

from client.models import MyUser
from client.permission import IsSystemAdmin, IsNonDeleteTeacher
from client.serializers import MyUserSerializer
from client.users.serializers import SystemUserSerializer
from mylib.my_common import MyDjangoFilterBackend


class ListCreateAdminCredentials(generics.CreateAPIView):
    serializer_class = SystemUserSerializer
    queryset = MyUser.objects.filter(is_superuser=False).prefetch_related("teacher", "teacher__school")
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = [IsAuthenticated, IsSystemAdmin]
    filter_mixin = UsersFilter

    def get_serializer_class(self):
        print("Getting serializer")
        if self.request.method == "GET":
            print("Ger")
            return MyUserSerializer
        print(self.request.method)
        return self.serializer_class


class RetrieveUpdateSystemUser(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MyUserSerializer
    queryset = MyUser.objects.filter(is_superuser=False)
    permission_classes = [IsAuthenticated, IsSystemAdmin, IsNonDeleteTeacher]
