from django.conf.urls import patterns, include, url
from django.contrib import admin
from rates import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ratesapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^v1/api/', include(v1_api)),
    url(r'^rates/', views.rates, name='rates'),
    url(r'^admin/', include(admin.site.urls)),
)
