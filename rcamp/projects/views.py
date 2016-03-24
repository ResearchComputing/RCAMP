from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
import ast

from lib.auth_mixin import LoginRequiredMixin
from mailer.signals import project_created_by_user
from projects.models import Project
from projects.forms import ProjectForm
from projects.forms import ProjectEditForm



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

    def form_valid(self, form):
        user = self.request.user
        managers = form.cleaned_data['managers']
        if user.username not in managers:
            managers = ast.literal_eval(managers)
            managers.append(user.username)
            managers = str(managers)
            form.cleaned_data.update({'managers':managers})
        proj = Project.objects.create(**form.cleaned_data)
        project_created_by_user.send(sender=proj.__class__,project=proj)
        self.success_url = reverse_lazy(
            'project-detail',
            kwargs={'pk':proj.pk}
        )
        return super(ProjectCreateView,self).form_valid(form)

class ProjectEditView(FormView, LoginRequiredMixin):
    template_name = 'project-edit.html'
    form_class = ProjectEditForm

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.object = get_object_or_404(Project,pk=pk)
        if request.user.username not in self.object.managers:
            return redirect('project-detail-view', pk=pk)
        else:
            return super(ProjectEditView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        pk = int(path_cmp[-2])
        self.object = get_object_or_404(Project,pk=pk)
        if request.user.username not in self.object.managers:
            return redirect('project-detail-view', pk=pk)
        else:
            return super(ProjectEditView,self).post(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProjectEditView, self).get_context_data(**kwargs)
        context['object'] = self.object
        return context

    def get_initial(self):
        initial = super(ProjectEditView,self).get_initial()
        initial['title'] = self.object.title
        initial['description'] = self.object.description
        initial['pi_emails'] = ','.join(self.object.pi_emails)
        initial['managers'] = self.object.managers
        initial['collaborators'] = self.object.collaborators
        return initial

    def form_valid(self, form):
        user = self.request.user
        managers = form.cleaned_data['managers']
        if user.username not in managers:
            managers = ast.literal_eval(managers)
            managers.append(user.username)
            managers = str(managers)
            form.cleaned_data.update({'managers':managers})
        proj = Project.objects.filter(
                pk=self.object.pk
            ).update(
                **form.cleaned_data
            )
        self.success_url = reverse_lazy(
            'project-detail',
            kwargs={'pk':self.object.pk}
        )
        return super(ProjectEditView,self).form_valid(form)
