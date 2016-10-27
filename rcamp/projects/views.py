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

from mailer.signals import project_created_by_user
from mailer.signals import allocation_request_created_by_user
from projects.models import Project
from projects.models import Reference
from projects.models import Allocation
from projects.models import AllocationRequest
from projects.forms import ProjectForm
from projects.forms import ProjectEditForm
from projects.forms import ReferenceForm
from projects.forms import AllocationRequestForm



class ProjectListView(ListView):
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

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project-detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        references = Reference.objects.filter(project=self.object)
        allocations = Allocation.objects.filter(project=self.object)
        allocation_requests = AllocationRequest.objects.filter(project=self.object)
        context['references'] = references
        context['allocations'] = allocations
        context['allocation_requests'] = allocation_requests
        return context

class ProjectCreateView(FormView):
    template_name = 'project-create.html'
    form_class = ProjectForm

    def form_valid(self, form):
        user = self.request.user
        managers = form.cleaned_data['managers']
        collaborators = form.cleaned_data['collaborators']
        if not collaborators:
            collaborators = []
        if user.username not in managers:
            if not managers:
                managers = []
            else:
                managers = ast.literal_eval(managers)
            managers.append(user.username)
            managers = str(managers)
            form.cleaned_data.update({
                'managers':managers,
                'collaborators': collaborators
            })
        proj = Project.objects.create(**form.cleaned_data)
        project_created_by_user.send(sender=proj.__class__,project=proj)
        self.success_url = reverse_lazy(
            'projects:project-detail',
            kwargs={'pk':proj.pk}
        )
        return super(ProjectCreateView,self).form_valid(form)

class ProjectEditView(FormView):
    template_name = 'project-edit.html'
    form_class = ProjectEditForm

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.object = get_object_or_404(Project,pk=pk)
        if request.user.username not in self.object.managers:
            return redirect('projects:project-detail', pk=pk)
        else:
            return super(ProjectEditView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        pk = int(path_cmp[-2])
        self.object = get_object_or_404(Project,pk=pk)
        if request.user.username not in self.object.managers:
            return redirect('projects:project-detail', pk=pk)
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
        collaborators = form.cleaned_data['collaborators']
        if not collaborators:
            collaborators = []
        if user.username not in managers:
            if not managers:
                managers = []
            else:
                managers = ast.literal_eval(managers)
            managers.append(user.username)
            managers = str(managers)
            form.cleaned_data.update({
                'managers':managers,
                'collaborators': collaborators
            })
        proj = Project.objects.filter(
                pk=self.object.pk
            ).update(
                **form.cleaned_data
            )
        self.success_url = reverse_lazy(
            'projects:project-detail',
            kwargs={'pk':self.object.pk}
        )
        return super(ProjectEditView,self).form_valid(form)

class ReferenceDetailView(DetailView):
    model = Reference
    template_name = 'reference-detail.html'

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        return super(ReferenceDetailView,self).get(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferenceDetailView,self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

class ReferenceCreateView(FormView):
    template_name = 'reference-create.html'
    form_class = ReferenceForm

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        if request.user.username not in self.project.managers:
            return redirect('projects:project-detail', pk=project_pk)
        else:
            return super(ReferenceCreateView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        project_pk = int(path_cmp[-3])
        self.project = get_object_or_404(Project,pk=project_pk)
        if request.user.username not in self.project.managers:
            return redirect('projects:project-detail', pk=project_pk)
        else:
            return super(ReferenceCreateView,self).post(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferenceCreateView,self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        ref_dict = {
            'project': self.project
        }
        ref_dict.update(form.cleaned_data)
        ref = Reference.objects.create(**ref_dict)
        self.success_url = reverse_lazy(
            'projects:reference-detail',
            kwargs={
                'project_pk':self.project.pk,
                'pk':ref.pk,
            }
        )
        return super(ReferenceCreateView,self).form_valid(form)

class ReferenceEditView(FormView):
    template_name = 'reference-edit.html'
    form_class = ReferenceForm

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        ref_pk = kwargs.get('pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        self.object = get_object_or_404(Reference,pk=ref_pk)
        if request.user.username not in self.project.managers:
            return redirect('projects:project-detail', pk=project_pk)
        else:
            return super(ReferenceEditView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        project_pk = int(path_cmp[-4])
        ref_pk = int(path_cmp[-2])
        self.project = get_object_or_404(Project,pk=project_pk)
        self.object = get_object_or_404(Reference,pk=ref_pk)
        if request.user.username not in self.project.managers:
            return redirect('projects:project-detail', pk=project_pk)
        else:
            return super(ReferenceEditView,self).post(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReferenceEditView,self).get_context_data(**kwargs)
        context['project'] = self.project
        context['object'] = self.object
        return context

    def get_initial(self):
        initial = super(ReferenceEditView,self).get_initial()
        initial['description'] = self.object.description
        initial['link'] = self.object.link
        return initial

    def form_valid(self, form):
        ref = Reference.objects.filter(
            pk=self.object.pk
        ).update(
            **form.cleaned_data
        )
        self.success_url = reverse_lazy(
            'projects:reference-detail',
            kwargs={
                'project_pk':self.project.pk,
                'pk':self.object.pk,
            }
        )
        return super(ReferenceEditView,self).form_valid(form)

class AllocationRequestCreateView(FormView):
    template_name = 'allocation-request-create.html'
    form_class = AllocationRequestForm

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        if request.user.username not in self.project.managers:
            return redirect('projects:project-detail', pk=project_pk)
        else:
            return super(AllocationRequestCreateView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        project_pk = int(path_cmp[-3])
        self.project = get_object_or_404(Project,pk=project_pk)
        if request.user.username not in self.project.managers:
            return redirect('projects:project-detail', pk=project_pk)
        else:
            return super(AllocationRequestCreateView,self).post(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllocationRequestCreateView,self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        ar_dict = {
            'project': self.project
        }
        ar_dict.update(form.cleaned_data)
        ar = AllocationRequest.objects.create(**ar_dict)
        allocation_request_created_by_user.send(sender=ar.__class__,allocation_request=ar)
        self.success_url = reverse_lazy(
            'projects:allocation-request-detail',
            kwargs={
                'project_pk':self.project.pk,
                'pk':ar.pk,
            }
        )
        return super(AllocationRequestCreateView,self).form_valid(form)

class AllocationRequestDetailView(DetailView):
    model = AllocationRequest
    template_name = 'allocation-request-detail.html'

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        return super(AllocationRequestDetailView,self).get(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllocationRequestDetailView,self).get_context_data(**kwargs)
        context['project'] = self.project
        return context
