
from rest_framework import  generics
from translation.models import TranslationText
from translation.translation_texts.serializers import TranslationTextSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination

class ListCreateTranslationTextsAPIView(generics.ListCreateAPIView):
    serializer_class = TranslationTextSerializer
    queryset = TranslationText.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)

class RetrieveUpdateDestroyTranslationTextAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TranslationTextSerializer
    queryset = TranslationText.objects.all()
    permission_classes = (IsAuthenticated,)
