from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from accounts.models import AccountRequest
from accounts.models import CuLdapUser
from accounts.forms import CuAccountRequestForm
from mailer.signals import account_request_received


# Create your views here.
class OrgSelectView(TemplateView):
    template_name = 'org-select.html'
    
    def get_context_data(self, **kwargs):
        context = super(OrgSelectView,self).get_context_data(**kwargs)
        context['organizations'] = (
            ('cu','University of Colorado Boulder'),
            # ('csu','Colorado State University'),
            ('xsede','XSEDE'),
        )
        return context

class CuAccountRequestCreateView(FormView):
    template_name = 'cu-account-request-create.html'
    form_class = CuAccountRequestForm
    
    def form_valid(self, form):
        # Authenticate here
        un = form.cleaned_data.get('username')
        user = CuLdapUser.objects.get(username=un)
        
        res_list = []
        for k in ['shared_compute','gpu','condo','petalibrary',]:
            if form.cleaned_data.get(k):
                res_list.append(k)
        
        ar_dict = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'organization': 'cu',
            'resources_requested': ','.join(res_list),
        }
        ar = AccountRequest.objects.get_or_create(**ar_dict)
        account_request_received.send(sender=ar.__class__,account_request=ar)
        
        self.success_url = reverse_lazy('account-request-review', kwargs={'request_id':ar[0].id})
        return super(CuAccountRequestCreateView,self).form_valid(form)

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
