
from rest_framework import  generics
from school.models import OoscPartner
from school.oosc_partners.serializers import OoscPartnerSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination

class ListCreateOoscPartnersAPIView(generics.ListCreateAPIView):
    serializer_class = OoscPartnerSerializer
    queryset = OoscPartner.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

class RetrieveUpdateDestroyOoscPartnerAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OoscPartnerSerializer
    queryset = OoscPartner.objects.all()
    permission_classes = (IsAuthenticated,)
