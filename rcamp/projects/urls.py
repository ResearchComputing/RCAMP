from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from projects.views import ProjectListView
from projects.views import ProjectDetailView
from projects.views import ProjectEditView
from projects.views import ProjectCreateView
from projects.views import ReferenceDetailView
from projects.views import ReferenceEditView
from projects.views import ReferenceCreateView

urlpatterns = [
    url(r'^list$', login_required(ProjectListView.as_view()), name='project-list'),
    url(r'^list/(?P<pk>[-\w]+)/$', login_required(ProjectDetailView.as_view()), name='project-detail'),
    url(r'^list/(?P<pk>[-\w]+)/edit$', login_required(ProjectEditView.as_view()), name='project-edit'),
    url(r'^create$', login_required(ProjectCreateView.as_view()), name='project-create'),
    url(r'^list/(?P<project_pk>[-\w]+)/references/(?P<pk>[-\w]+)/$', login_required(ReferenceDetailView.as_view()), name='reference-detail'),
    url(r'^list/(?P<project_pk>[-\w]+)/references/(?P<pk>[-\w]+)/edit$', login_required(ReferenceEditView.as_view()), name='reference-edit'),
    url(r'^list/(?P<project_pk>[-\w]+)/references/create$', login_required(ReferenceCreateView.as_view()), name='reference-create'),
]
