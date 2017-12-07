import copy
from django.http import (
    HttpResponse,
    HttpResponseRedirect
)
from django.template import loader
from django.shortcuts import render
from django.views.generic import (
    View,
    ListView,
    DetailView
)
from django.views.generic.edit import (
    FormView,
    UpdateView
)
from django.db.models import Q
import django.utils.http
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect

from mailer.signals import project_created_by_user
from mailer.signals import allocation_request_created_by_user

from accounts.models import (
    User,
    RcLdapUser
)

from projects.models import (
    Project,
    Reference,
    Allocation,
    AllocationRequest
)
from projects.forms import (
    ProjectForm,
    ProjectEditForm,
    ReferenceForm,
    AllocationRequestForm
)


GENERAL_ACCOUNT_REQUEST_SUBJECT = "{general_account} account request: {username}"
GENERAL_ACCOUNT_REQUEST_BODY = "Please add me ({username}) to the {general_account} account. I will use it to [insert reason or activity here]."


class ProjectAccessMixin(object):
    def is_manager(self,request_user,project):
        is_manager = False
        if request_user in project.managers.all():
            is_manager = True
        return is_manager

    def get_manager_or_redirect(self,request_user,project,redirect_view='projects:project-detail'):
        if not self.is_manager(request_user,project):
            return redirect(redirect_view, pk=project.pk)
        return request_user

class ProjectListView(ListView):
    model = Project
    template_name = 'project-list.html'

    def get_queryset(self):
        user = self.request.user
        manager_on = user.manager_on.all()
        collaborator_on = user.collaborator_on.all()
        projects = (manager_on | collaborator_on).distinct()
        return projects

    def get_context_data(self, **kwargs):
        context = super(ProjectListView,self).get_context_data(**kwargs)

        user = self.request.user
        general_account = '{}-general'.format(user.organization)
        context['general_account'] = general_account
        context['general_request_subject'] = GENERAL_ACCOUNT_REQUEST_SUBJECT.format(username=user.username, general_account=general_account)
        context['general_request_body'] = GENERAL_ACCOUNT_REQUEST_BODY.format(username=user.username, general_account=general_account)

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
        creator = self.request.user
        project = form.save()
        if not project.managers.filter(username=creator.username).exists():
            project.managers.add(creator)
        project.save()
        project_created_by_user.send(sender=project.__class__, project=project)
        self.success_url = reverse_lazy(
            'projects:project-detail',
            kwargs={'pk':project.pk},
        )
        # Avoid calling save() multiple times, so return response directly instead
        # of calling super() and letting the FormMixin class do so.
        return HttpResponseRedirect(self.success_url)


class ProjectEditView(UpdateView,ProjectAccessMixin):
    template_name = 'project-edit.html'
    model = Project
    form_class = ProjectEditForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProjectEditView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.object = get_object_or_404(Project,pk=pk)
        manager = self.get_manager_or_redirect(request.user,self.object)
        return super(ProjectEditView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        pk = int(path_cmp[-2])
        self.object = get_object_or_404(Project,pk=pk)
        manager = self.get_manager_or_redirect(request.user,self.object)
        return super(ProjectEditView,self).post(request,*args,**kwargs)

    def get_initial(self):
        initial = super(ProjectEditView,self).get_initial()
        initial['pi_emails'] = ','.join(self.object.pi_emails)
        return initial

    def form_valid(self, form):
        editor = self.request.user
        project = form.save()
        if not project.managers.filter(username=editor.username).exists():
            project.managers.add(editor)
        project.save()
        self.success_url = reverse_lazy(
            'projects:project-detail',
            kwargs={'pk':self.object.pk}
        )
        return HttpResponseRedirect(self.success_url)


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

class ReferenceCreateView(FormView,ProjectAccessMixin):
    template_name = 'reference-create.html'
    form_class = ReferenceForm

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        manager = self.get_manager_or_redirect(request.user,self.project)
        return super(ReferenceCreateView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        project_pk = int(path_cmp[-3])
        self.project = get_object_or_404(Project,pk=project_pk)
        manager = self.get_manager_or_redirect(request.user,self.project)
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

class ReferenceEditView(FormView,ProjectAccessMixin):
    template_name = 'reference-edit.html'
    form_class = ReferenceForm

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        ref_pk = kwargs.get('pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        self.object = get_object_or_404(Reference,pk=ref_pk)
        manager = self.get_manager_or_redirect(request.user,self.project)
        return super(ReferenceEditView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        project_pk = int(path_cmp[-4])
        ref_pk = int(path_cmp[-2])
        self.project = get_object_or_404(Project,pk=project_pk)
        self.object = get_object_or_404(Reference,pk=ref_pk)
        manager = self.get_manager_or_redirect(request.user,self.project)
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

class AllocationRequestCreateView(FormView,ProjectAccessMixin):
    template_name = 'allocation-request-create.html'
    form_class = AllocationRequestForm

    def get(self, request, *args, **kwargs):
        project_pk = kwargs.get('project_pk')
        self.project = get_object_or_404(Project,pk=project_pk)
        manager = self.get_manager_or_redirect(request.user,self.project)
        return super(AllocationRequestCreateView,self).get(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        path_cmp = self.request.path.split('/')
        project_pk = int(path_cmp[-3])
        self.project = get_object_or_404(Project,pk=project_pk)
        manager = self.get_manager_or_redirect(request.user,self.project)
        return super(AllocationRequestCreateView,self).post(request,*args,**kwargs)

    def get_context_data(self, **kwargs):
        context = super(AllocationRequestCreateView,self).get_context_data(**kwargs)
        context['project'] = self.project
        return context

    def form_valid(self, form):
        ar_dict = {
            'project': self.project,
            'requester': self.request.user
        }
        ar_dict.update(form.cleaned_data)
        ar = AllocationRequest.objects.create(**ar_dict)

        try:
            requester = RcLdapUser.objects.get(username=ar.requester.username)
        except RcLdapUser.DoesNotExist:
            requester = None

        allocation_request_created_by_user.send(sender=ar.__class__,allocation_request=ar,requester=requester)
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
