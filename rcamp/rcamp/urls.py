"""rcamp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.conf.urls import handler404
from django.conf.urls import handler500
from django.conf import settings
# Make sure signals/receivers get loaded.
from mailer import receivers
from projects import receivers
from lib.views import index_view



handler404 = 'lib.views.handler404'
handler500 = 'lib.views.handler500'

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^$', index_view, name='index'),
    url(r'^login', auth_views.login, {'template_name':'login.html'}),
    url(r'^logout', auth_views.logout, {'template_name':'logout.html'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('endpoints.urls')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^projects/', include('projects.urls', namespace='projects')),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
