from django.conf.urls import include, url
from projects.views import ProjectListView
from projects.views import ProjectDetailView

urlpatterns = [
    url(r'^list$', ProjectListView.as_view(), name='project-list'),
    url(r'^list/(?P<pk>[-\w]+)/$', ProjectDetailView.as_view(), name='project-detail'),
]
