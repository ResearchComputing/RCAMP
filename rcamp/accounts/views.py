from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from accounts.models import AccountRequest
from accounts.models import CuLdapUser
from accounts.forms import AccountRequestForm
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
            pass
        elif org =='xsede':
            pass
        login_shell = form.cleaned_data.get('login_shell')
        role = form.cleaned_data.get('role')

        res_list = []
        for k in ['blanca','janus','summit','petalibrary_active','petalibrary_archive',]:
            if form.cleaned_data.get(k):
                res_list.append(k)

        ar_dict = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': role,
            'organization': org,
            'login_shell': login_shell,
            'resources_requested': ','.join(res_list),
        }
        ar = AccountRequest.objects.get_or_create(**ar_dict)
        account_request_received.send(sender=ar.__class__,account_request=ar)

        self.success_url = reverse_lazy('account-request-review', kwargs={'request_id':ar[0].id})
        return super(AccountRequestCreateView,self).form_valid(form)

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
