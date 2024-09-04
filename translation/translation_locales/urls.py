from django.conf.urls import url
from translation.translation_locales.views import ListCreateTranslationLocalesAPIView, ListTranslationFlutterFormattedLocalesAPIView, RetrieveUpdateDestroyTranslationLocaleAPIView

urlpatterns = [
    url(r"^$", ListCreateTranslationLocalesAPIView.as_view(), name="list_create_translation_locales"),
    url(r"^flutter/?$", ListTranslationFlutterFormattedLocalesAPIView.as_view(), name="list_flutter_formatted_translation_locales"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroyTranslationLocaleAPIView.as_view(), name="retrieve_update_destroy_translation_locale"),
]
