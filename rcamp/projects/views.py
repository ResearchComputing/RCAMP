from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from lib.auth_mixin import LoginRequiredMixin
from projects.models import Project
from projects.forms import ProjectForm



class ProjectListView(ListView, LoginRequiredMixin):
    model = Project
    template_name = 'project-list.html'

    def get_queryset(self):
        user = self.request.user.username
        return Project.objects.filter(
            Q(collaborators__contains=user) | Q(managers__contains=user)
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

class ProjectDetailView(DetailView, LoginRequiredMixin):
    model = Project
    template_name = 'project-detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        return context

class ProjectCreateView(FormView, LoginRequiredMixin):
    template_name = 'project-create.html'
    form_class = ProjectForm

    def form_valid(self,form):
        proj = Project.objects.create(**form.cleaned_data)
        self.success_url = reverse_lazy(
            'project-detail',
            kwargs={'pk':proj.pk}
        )
        return super(ProjectCreateView,self).form_valid(form)
