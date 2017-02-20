from django.contrib import admin
from django import forms
from django.template import Template,Context
from django.core.exceptions import ValidationError
from mailer.models import MailNotifier
from mailer.models import MailLog



class MailNotifierAdminForm(forms.ModelForm):
    class Meta:
        model = MailNotifier
        exclude = ()

    def clean(self):
        super(MailNotifierAdminForm,self).clean()

        tpl_fields = ['subject','body','mailto','cc','bcc']
        for field in tpl_fields:
            try:
                t = Template(self.cleaned_data[field])
                c = Context({})
                t.render(c)
            except:
                raise ValidationError('Cannot save notifier because there is a template error in the {} field.'.format(field))

@admin.register(MailNotifier)
class MailNotifierAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Notifier Details', {
            'fields': ('name','event')
            }),
        ('Recipients and Sender', {
            'fields': ('from_address','mailto','cc','bcc'),
            'description': """
            A comma-separated list of addresses.
            """
            }),
        ('Message Details', {
            'fields': ('subject','body')
        }),
    )
    form = MailNotifierAdminForm

@admin.register(MailLog)
class MailLogAdmin(admin.ModelAdmin):
    list_display = [
        'recipient_emails',
        'date_sent',
        'reference_name',
        'from_host'
    ]
    search_fields = [
        'date_sent',
        'recipient_emails',
        'reference_name',
        'from_host'
    ]
