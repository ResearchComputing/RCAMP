from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from accounts.models import AccountRequest

# Create your views here.
class OrgSelectView(TemplateView):
    template_name = "org-select.html"
    
    def get_context_data(self, **kwargs):
        context = super(OrgSelectView,self).get_context_data(**kwargs)
        context['organizations'] = (
            ('ucb','University of Colorado Boulder'),
            ('csu','Colorado State University'),
            ('xsede','XSEDE'),
        )
        return context
