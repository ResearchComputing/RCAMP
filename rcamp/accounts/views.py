from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from accounts.models import AccountRequest
from accounts.models import CuLdapUser
from accounts.models import CsuLdapUser
from projects.models import Project
from accounts.forms import AccountRequestForm
from accounts.forms import SponsoredAccountRequestForm
from accounts.forms import ClassAccountRequestForm
from accounts.forms import ProjectAccountRequestForm
from mailer.signals import account_request_received


# Create your views here.
class ReasonView(TemplateView):
    template_name = 'reason.html'

    def get_context_data(self, **kwargs):
        context = super(ReasonView,self).get_context_data(**kwargs)
        return context

class AccountRequestCreateView(FormView):
    template_name = 'account-request-create.html'
    form_class = AccountRequestForm

    def form_valid(self, form):
        org = form.cleaned_data.get('organization')
        un = form.cleaned_data.get('username')
        if org == 'ucb':
            user = CuLdapUser.objects.get(username=un)
        elif org == 'csu':
            user = CsuLdapUser.objects.get(username=un)
        elif org =='xsede':
            pass
        login_shell = form.cleaned_data.get('login_shell')
        role = form.cleaned_data.get('role')

        res_list = []
        for k in ['blanca','janus','summit','petalibrary_active','petalibrary_archive',]:
            if form.cleaned_data.get(k):
                res_list.append(k)

        if not hasattr(self, 'ar_dict'):
            self.ar_dict = {}
        self.ar_dict.update({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': role,
            'organization': org,
            'login_shell': login_shell,
            'resources_requested': ','.join(res_list),
        })

        # Check for m2m fields
        m2m_dict = {}
        for k in self.ar_dict.keys():
            if k.startswith('m2m_'):
                new_key = k.replace('m2m_','')
                val = self.ar_dict.pop(k)
                m2m_dict[new_key] = val

        ar, created = AccountRequest.objects.get_or_create(**self.ar_dict)

        # Add m2m values
        for key, val in m2m_dict.iteritems():
            for v in val:
                m2m_field = getattr(ar,key)
                m2m_field.add(v)
            ar.save()

        account_request_received.send(sender=ar.__class__,account_request=ar)

        # Auto-approve CSU requests
        if org == 'csu':
            #Force AR to load from db
            ar_loaded = AccountRequest.objects.get(username=user.username,organization=org)

            ar_loaded.status = 'a'
            ar_loaded.save()

        self.success_url = reverse_lazy('accounts:account-request-review', kwargs={'request_id':ar.id})
        return super(AccountRequestCreateView,self).form_valid(form)

class SponsoredAccountRequestCreateView(AccountRequestCreateView):
    template_name = 'sponsored-account-request-create.html'
    form_class = SponsoredAccountRequestForm

    def form_valid(self, form):
        sponsor_email = form.cleaned_data.get('sponsor_email')
        if not hasattr(self, 'ar_dict'):
            self.ar_dict = {}
        self.ar_dict['sponsor_email'] = sponsor_email
        return super(SponsoredAccountRequestCreateView,self).form_valid(form)

class ClassAccountRequestCreateView(AccountRequestCreateView):
    template_name = 'class-account-request-create.html'
    form_class = ClassAccountRequestForm

    def form_valid(self, form):
        course_number = form.cleaned_data.get('course_number')
        if not hasattr(self, 'ar_dict'):
            self.ar_dict = {}
        self.ar_dict['course_number'] = course_number
        return super(ClassAccountRequestCreateView,self).form_valid(form)

class ProjectAccountRequestCreateView(AccountRequestCreateView):
    template_name = 'project-account-request-create.html'
    form_class = ProjectAccountRequestForm

    def form_valid(self, form):
        projs = form.cleaned_data.get('projects')
        if not hasattr(self, 'ar_dict'):
            self.ar_dict = {}
        self.ar_dict['m2m_projects'] = projs
        return super(ProjectAccountRequestCreateView,self).form_valid(form)

class AccountRequestReviewView(TemplateView):
    template_name = 'account-request-review.html'

    def get_context_data(self, **kwargs):
        request_id = kwargs.get('request_id')
        try:
            context = super(AccountRequestReviewView,self).get_context_data(**kwargs)
            ar = AccountRequest.objects.get(id=request_id)
            context['account_request'] = ar
            return context
        except AccountRequest.DoesNotExist:
            raise Http404('Account Request not found.')
