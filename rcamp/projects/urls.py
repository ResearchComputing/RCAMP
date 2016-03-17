from django.conf.urls import include, url
from projects.views import ProjectListView

urlpatterns = [
    url(r'^list$', ProjectListView.as_view(), name='project-list'),
]
