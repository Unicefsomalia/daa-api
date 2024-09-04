
from django.conf.urls import url
from school.oosc_partners.views import ListCreateOoscPartnersAPIView, RetrieveUpdateDestroyOoscPartnerAPIView
urlpatterns=[
    url(r'^$',ListCreateOoscPartnersAPIView.as_view(),name="list_create_oosc_partners"),
    url(r'^(?P<pk>[0-9]+)/?$',RetrieveUpdateDestroyOoscPartnerAPIView.as_view(),name="retrieve_update_destroy_oosc_partner"),
]
