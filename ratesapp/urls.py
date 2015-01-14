from django.conf.urls import patterns, include, url
from django.contrib import admin
from rates import views
from django.views.generic import TemplateView


urlpatterns = patterns('api/v1/',
    # Examples:
    # url(r'^$', 'ratesapp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^api/label/', views.label, name='label'),
    url(r'^api/rates/$', views.rates, name='rates'),
    url(r'^api/v1/', TemplateView.as_view(template_name="base.html")),
    url(r'^admin/', include(admin.site.urls)),
)
