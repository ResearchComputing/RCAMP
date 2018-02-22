from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from accounts.models import (
    AccountRequest,
    CuLdapUser,
    CsuLdapUser
)
from accounts.forms import (
    AccountRequestUcbForm,
    AccountRequestIntentForm
)
from mailer.signals import account_request_received



class OrgSelectView(TemplateView):
    template_name = 'org-select.html'

    def get_context_data(self, **kwargs):
        context = super(OrgSelectView,self).get_context_data(**kwargs)
        return context


class AccountRequestCreateUcbView(FormView):
    template_name = 'account-request-create-ucb.html'
    form_class = AccountRequestUcbForm

    def form_valid(self, form):
        organization = 'ucb'
        username = form.cleaned_data.get('username')
        cu_user = CuLdapUser.objects.get(username=username)
        department = form.cleaned_data.get('department')
        role = form.cleaned_data.get('role')

        account_request_dict = dict(
            username = cu_user.username,
            first_name = cu_user.first_name,
            last_name = cu_user.last_name,
            email = cu_user.email,
            department = department,
            role = role,
            organization = organization,
        )

        # Auto-approve eligible users
        if cu_user.edu_affiliation.lower() in ['student','staff','faculty']:
            account_request_dict['status'] = 'a'

        self.request.session['account_request_dict'] = account_request_dict
        self.success_url = reverse_lazy('accounts:account-request-intent')
        return super(AccountRequestCreateUcbView,self).form_valid(form)

class AccountRequestIntentView(FormView):
    template_name = 'account-request-intent.html'
    form_class = AccountRequestIntentForm

    def form_valid(self, form):
        pass
