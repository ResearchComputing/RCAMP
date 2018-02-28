from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.base import ContextMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from accounts.models import (
    AccountRequest,
    Intent,
    CuLdapUser,
    CsuLdapUser
)
from accounts.forms import (
    AccountRequestVerifyUcbForm,
    AccountRequestVerifyCsuForm,
    AccountRequestIntentForm
)
from mailer.signals import account_request_received



class AccountRequestOrgSelectView(TemplateView):
    template_name = 'account-request-org-select.html'

    def get_context_data(self, **kwargs):
        context = super(AccountRequestOrgSelectView,self).get_context_data(**kwargs)
        return context


class AccountRequestVerifyUcbView(FormView):
    template_name = 'account-request-verify-ucb.html'
    form_class = AccountRequestVerifyUcbForm

    def _check_autoapprove_eligibility(self, user_affiliation):
        """
        Takes an eduPersonAffiliation attribute and returns True if it contains values that are
        eligible for auto-approval.
        """
        eligible_affiliations = ['student','staff','faculty']
        eligible = False
        for affiliation in user_affiliation:
            if affiliation.lower() in eligible_affiliations:
                eligible = True
        return eligible

    def form_valid(self, form):
        organization = 'ucb'
        username = form.cleaned_data.get('username')
        cu_user = CuLdapUser.objects.get(username=username)
        department = form.cleaned_data.get('department')
        role = form.cleaned_data.get('role')

        account_request_data = dict(
            username = cu_user.username,
            first_name = cu_user.first_name,
            last_name = cu_user.last_name,
            email = cu_user.email,
            department = department,
            role = role,
            organization = organization,
        )

        # Auto-approve eligible users
        if self._check_autoapprove_eligibility(cu_user.edu_affiliation):
            account_request_data['status'] = 'a'

        self.request.session['account_request_data'] = account_request_data
        self.success_url = reverse_lazy('accounts:account-request-intent')
        return super(AccountRequestVerifyUcbView,self).form_valid(form)


class AccountRequestVerifyCsuView(FormView):
    template_name = 'account-request-verify-csu.html'
    form_class = AccountRequestVerifyCsuForm

    def form_valid(self, form):
        organization = 'csu'
        username = form.cleaned_data.get('username')
        csu_user = CsuLdapUser.objects.get(username=username)
        department = form.cleaned_data.get('department')
        role = form.cleaned_data.get('role')

        account_request_data = dict(
            username = csu_user.username,
            first_name = csu_user.first_name,
            last_name = csu_user.last_name,
            email = csu_user.email,
            department = department,
            role = role,
            organization = organization
        )

        # Auto-approve all CSU users
        account_request_data['status'] = 'a'

        self.request.session['account_request_data'] = account_request_data
        self.success_url = reverse_lazy('accounts:account-request-intent')
        return super(AccountRequestVerifyCsuView,self).form_valid(form)


class AccountRequestIntentView(FormView):
    template_name = 'account-request-intent.html'
    form_class = AccountRequestIntentForm

    def form_valid(self, form):
        account_request_data = self.request.session['account_request_data']
        account_request = AccountRequest.objects.create(**account_request_data)
        if account_request.status != 'a':
            account_request_received.send(sender=account_request.__class__,account_request=account_request)
        self.request.session['account_request_data']['id'] = account_request.id
        self.request.session.save()

        try:
            intent_dict = dict(
                account_request = account_request,
                **form.cleaned_data
            )
            intent = Intent.objects.create(**intent_dict)
        except:
            # TODO: Add proper logging here, but don't make the request fail
            # if creating the Intent object does.
            pass

        self.success_url = reverse_lazy('accounts:account-request-review')
        return super(AccountRequestIntentView,self).form_valid(form)


class AccountRequestReviewView(TemplateView):
    template_name = 'account-request-review.html'

    def get_context_data(self, **kwargs):
        try:
            context = super(AccountRequestReviewView,self).get_context_data(**kwargs)
            account_request_data = self.request.session.get('account_request_data',None)
            if not account_request_data:
                raise Http404('No session data.')
            request_id = account_request_data.get('id',None)
            account_request = AccountRequest.objects.get(id=request_id)
            context['account_request'] = account_request
            return context
        except AccountRequest.DoesNotExist:
            raise Http404('Account Request not found.')
