from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from project.models import Project



@login_required
class ProjectListView(ListView):
    model = Project
    template_name = "project-list.html"

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(
            Q(collaborators__in=user) | Q(managers__in=user)
        )

    def get_context_data(self, **kwargs):
        context = super(ProjectListView,self).get_context_data(**kwargs)
        return context
