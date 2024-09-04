from django.conf.urls import url

from school.views import ListCreateSchoolsAPIView, ListSearchSchoolsAPIView, RetrieveUpdateDestroySchoolAPIView, ImportSchoolData, MoeTestSchool, ListCreateSchoolsDynamicsAPIView

urlpatterns = [
    url(r"^$", ListCreateSchoolsAPIView.as_view(), name="list_create_schools"),
    url(r"^search/?$", ListSearchSchoolsAPIView.as_view(), name="list_search_schools"),
    url(r"^moe-test/?", MoeTestSchool.as_view(), name="moe_test"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroySchoolAPIView.as_view(), name="retrieve_update_destroy_school"),
    url(r"^stats/(?P<type>.+)", ListCreateSchoolsDynamicsAPIView.as_view(), name="list_create_schools_stats"),
    url(r"^import/?$", ImportSchoolData.as_view(), name="import_school_data"),
    # url(r'^(?P<pk>[0-9]+)/districts/?$', ListSchoolDistricts.as_view(), name="list_school_districts"),
]
