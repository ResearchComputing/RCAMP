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
        user = self.request.user.username
        return Project.objects.filter(
            Q(collaborators__in=user) | Q(managers__in=user)
        )

    def get_context_data(self, **kwargs):
        # user = self.request.user
        context = super(ProjectListView,self).get_context_data(**kwargs)
        # try:
        #     startup = Project.objects.get(
        #         pi_emails__in=user.email,
        #         is_startup=True
        #     )
        # except Project.DoesNotExist:
        #     startup = None
        # context['startup'] = startup
        return context
