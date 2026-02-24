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
from django.urls import include, re_path
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
    re_path(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    re_path(r'^$', index_view, name='index'),
    re_path(r'^login', auth_views.LoginView.as_view(template_name='registration/login.html')),
    re_path(r'^logout', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/', include('endpoints.urls')),
    re_path(r'^accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    re_path(r'^projects/', include(('projects.urls', 'projects'), namespace='projects')),
]


if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()
