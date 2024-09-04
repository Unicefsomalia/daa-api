from rest_framework import generics
from translation.models import LocaleTranslationText, TranslationLocale
from translation.translation_locales.serializers import TranslationLocaleSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination
from rest_framework.response import Response


class ListCreateTranslationLocalesAPIView(generics.ListCreateAPIView):
    serializer_class = TranslationLocaleSerializer
    queryset = TranslationLocale.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)


class RetrieveUpdateDestroyTranslationLocaleAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TranslationLocaleSerializer
    queryset = TranslationLocale.objects.all()
    permission_classes = (IsAuthenticated,)


class ListTranslationFlutterFormattedLocalesAPIView(generics.ListAPIView):
    serializer_class = TranslationLocaleSerializer
    queryset = TranslationLocale.objects.filter(active=True)
    filter_backends = (MyDjangoFilterBackend,)
    # permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = list(self.filter_queryset(self.get_queryset()))
        data = {}
        for locale in queryset:
            locale_properties = {}
            locale_key_name = f"{locale.language_code}_{locale.country_code}"

            locale_properties["language_name"] = locale.name
            translation_texts = list(LocaleTranslationText.objects.filter(locale_id=locale.id))

            for tr_tex in translation_texts:
                original = tr_tex.text.title
                translated = tr_tex.translated_text
                if translated != None:
                    locale_properties[original] = translated
            data[locale_key_name] = locale_properties

        return Response(data)
