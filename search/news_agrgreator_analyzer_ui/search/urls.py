from django.conf.urls import url

from . import views

app_name = 'search'
urlpatterns = [
    url(r'^news/detailed/(?P<pk>[0-9]+)/$', views.detailed_view, name='get_detailed_view'),
    url(r'^$', views.get_search, name='get_search'),
    url(r'^privacy/$', views.privacy, name='get_privacy'),
    url(r'^contact/$', views.contact_us, name='get_contact_us'),
    url(r'^about/$', views.about_us, name='get_about_us'),
]
