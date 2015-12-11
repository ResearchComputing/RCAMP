from django.contrib import admin
from mailer.models import MailNotifier
from mailer.models import MailLog


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

