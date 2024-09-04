
from django.conf.urls import url
from region.sub_countys.views import ListCreateSubCountysAPIView, RetrieveUpdateDestroySubCountyAPIView
urlpatterns=[
    url(r'^$',ListCreateSubCountysAPIView.as_view(),name="list_create_sub_countys"),
    url(r'^(?P<pk>[0-9]+)/?$',RetrieveUpdateDestroySubCountyAPIView.as_view(),name="retrieve_update_destroy_sub_county"),
]
