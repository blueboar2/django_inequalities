from django.conf.urls import patterns, include, url

from django.views.generic import TemplateView
from django.contrib import admin
from inequality import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^user/login/', 'django.contrib.auth.views.login'),
    url(r'^user/logout/', 'django.contrib.auth.views.logout', {'next_page': '/wsgi/'}),
    url(r'^$', views.tests),
    url(r'^tests/(?P<testassignnum>\d+)/$', views.runtest),
    url(r'^try/$', views.trytoanswer),
    url(r'^assign/$', views.assignajax),
    url(r'^admin/', include(admin.site.urls)),
)
