from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy
from accounts.models import AccountRequest
from accounts.models import CuLdapUser
from accounts.forms import CuAuthForm

# Create your views here.
class OrgSelectView(TemplateView):
    template_name = 'org-select.html'
    
    def get_context_data(self, **kwargs):
        context = super(OrgSelectView,self).get_context_data(**kwargs)
        context['organizations'] = (
            ('ucb','University of Colorado Boulder'),
            ('csu','Colorado State University'),
            ('xsede','XSEDE'),
        )
        return context

class CuAccountRequestCreateView(FormView):
    template_name = 'cu-account-request-create.html'
    form_class = CuAuthForm
    # success_url = reverse_lazy('account-request-review')
    
    def form_valid(self, form):
        # Authenticate here
        un = form.cleaned_data.get('username')
        user = CuLdapUser.objects.get(username=un)
        ar_dict = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'organization': 'cu',
        }
        ar = AccountRequest.objects.get_or_create(**ar_dict)
        
        self.success_url = reverse_lazy('account-request-review', kwargs={'request_id':ar[0].id})
        return super(CuAccountRequestCreateView,self).form_valid(form)

class AccountRequestReviewView(TemplateView):
    template_name = 'account-request-review.html'
    
    def get_context_data(self, **kwargs):
        request_id = kwargs.get('request_id')
        context = super(AccountRequestReviewView,self).get_context_data(**kwargs)
        ar = AccountRequest.objects.get(id=request_id)
        context['account_request'] = ar
        return context
