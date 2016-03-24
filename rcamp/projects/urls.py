from django.conf.urls import include, url
from projects.views import ProjectListView
from projects.views import ProjectDetailView
from projects.views import ProjectEditView
from projects.views import ProjectCreateView

urlpatterns = [
    url(r'^list$', ProjectListView.as_view(), name='project-list'),
    url(r'^list/(?P<pk>[-\w]+)/$', ProjectDetailView.as_view(), name='project-detail'),
    url(r'^list/(?P<pk>[-\w]+)/edit$', ProjectEditView.as_view(), name='project-edit'),
    url(r'^create$', ProjectCreateView.as_view(), name='project-create'),
]
