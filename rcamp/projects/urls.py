from django.urls import include, re_path
from django.contrib.auth.decorators import login_required
from projects.views import ProjectListView
from projects.views import ProjectDetailView
from projects.views import ProjectEditView
from projects.views import ProjectCreateView
from projects.views import ReferenceDetailView
from projects.views import ReferenceEditView
from projects.views import ReferenceCreateView
from projects.views import AllocationRequestDetailView
from projects.views import AllocationRequestCreateView

urlpatterns = [
    re_path(r'^list$', login_required(ProjectListView.as_view()), name='project-list'),
    re_path(r'^list/(?P<pk>[-\w]+)/$', login_required(ProjectDetailView.as_view()), name='project-detail'),
    re_path(r'^list/(?P<pk>[-\w]+)/edit$', login_required(ProjectEditView.as_view()), name='project-edit'),
    re_path(r'^create$', login_required(ProjectCreateView.as_view()), name='project-create'),
    re_path(r'^list/(?P<project_pk>[-\w]+)/references/(?P<pk>[-\w]+)/$', login_required(ReferenceDetailView.as_view()), name='reference-detail'),
    re_path(r'^list/(?P<project_pk>[-\w]+)/references/(?P<pk>[-\w]+)/edit$', login_required(ReferenceEditView.as_view()), name='reference-edit'),
    re_path(r'^list/(?P<project_pk>[-\w]+)/references/create$', login_required(ReferenceCreateView.as_view()), name='reference-create'),
    re_path(r'^list/(?P<project_pk>[-\w]+)/allocationrequests/(?P<pk>[-\w]+)/$', login_required(AllocationRequestDetailView.as_view()), name='allocation-request-detail'),
    re_path(r'^list/(?P<project_pk>[-\w]+)/allocationrequests/create$', login_required(AllocationRequestCreateView.as_view()), name='allocation-request-create'),
]
