
from rest_framework import  generics
from school.models import SchoolsStudentsImport
from school.schools_students_imports.serializers import SchoolsStudentsImportSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination
import os
class ListCreateSchoolsStudentsImportsAPIView(generics.ListCreateAPIView):
    serializer_class = SchoolsStudentsImportSerializer
    queryset = SchoolsStudentsImport.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
      name=serializer.validated_data.get("name")
      import_file=serializer.validated_data.get("import_file")
      filename, file_extension = os.path.splitext(import_file.name)
      # print(name,filename)
      if name ==None:
        name=filename

      serializer.save(user_id=self.request.user.id,name=name)

class RetrieveUpdateDestroySchoolsStudentsImportAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SchoolsStudentsImportSerializer
    queryset = SchoolsStudentsImport.objects.all()
    permission_classes = (IsAuthenticated,)


