from rest_framework import generics
from translation.models import LOCALE_TRANSLATIONS_TEXTS_DEFAULT_FIELDS, LOCALE_TRANSLATIONS_TEXTS_STATS_DEFINTIONS, LocaleTranslationText
from translation.locale_translation_texts.serializers import LocaleTranslationTextSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination
from stats.views import MyCustomDyamicStats
from drf_autodocs.decorators import format_docstring

LOCALE_TEXT_TRANSLATION_FILTERS = [
    {
        "field_name": "translated_text",
        "label": "Not Translated",
        "field_type": "bool",
        "lookup_expr": "isnull",
    },
    {
        "field_name": "text__title",
        "label": "Original",
        "field_type": "char",
    },
]


class ListCreateLocaleTranslationTextsAPIView(generics.ListCreateAPIView):
    serializer_class = LocaleTranslationTextSerializer
    queryset = LocaleTranslationText.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    extra_filter_fields = LOCALE_TEXT_TRANSLATION_FILTERS


class RetrieveUpdateDestroyLocaleTranslationTextAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LocaleTranslationTextSerializer
    queryset = LocaleTranslationText.objects.all()
    permission_classes = (IsAuthenticated,)


SUPPOERTED_TRANSLATION_STAT_TYES = [stat for stat in LOCALE_TRANSLATIONS_TEXTS_STATS_DEFINTIONS]


@format_docstring({}, stat_types=", ".join(SUPPOERTED_TRANSLATION_STAT_TYES))
class ListLocaleTranslationTextDynamicsAPIView(MyCustomDyamicStats, generics.ListCreateAPIView):
    """
    Group statistics by:
    `type` = {stat_types}
    """

    serializer_class = LocaleTranslationTextSerializer
    queryset = LocaleTranslationText.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    stat_type = ""
    count_name = "total"
    stats_definitions = LOCALE_TRANSLATIONS_TEXTS_STATS_DEFINTIONS
    default_fields = LOCALE_TRANSLATIONS_TEXTS_DEFAULT_FIELDS
    extra_filter_fields = LOCALE_TEXT_TRANSLATION_FILTERS
