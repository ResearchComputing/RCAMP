from django.db import models

from django.core import mail
from django.template import Template,Context
import time
import socket

import mailer.signals


MODULE_EXCLUDES = ['__builtins__', '__doc__', '__file__', '__name__', '__package__','django']
EVENT_CHOICES = tuple((s,s) for s in dir(mailer.signals) if s not in MODULE_EXCLUDES)

class MailNotifier(models.Model):
    name = models.CharField(max_length=128)
    event = models.CharField(max_length=128,choices=EVENT_CHOICES)

    mailto=models.TextField(null=True,blank=True)
    cc=models.TextField(null=True,blank=True)
    bcc=models.TextField(null=True,blank=True)
    from_address=models.EmailField(null=True,blank=True)

    subject = models.CharField(max_length=256)
    body = models.TextField()


    def send(self,context={}):
        m = self.make_email(context)
        m.send()

        mail_log = MailLog(
            reference_name=self.name,
            email_object=m.message().__str__(),
            recipient_emails=','.join(self.make_mailto_list(context)),
            from_host=socket.gethostname()
            )
        mail_log.save()

        return m.message()

    def make_email(self,context):

        email = mail.EmailMessage(subject=self.make_subject(context),
                                    body=self.make_body(context),
                                    from_email=self.from_address,
                                    to=self.make_mailto_list(context),
                                    cc=self.make_cc_list(context),
                                    bcc=self.make_bcc_list(context))
        return email

    def make_mailto_list(self,context={}):
        t = Template(self.mailto)
        c = Context(context)
        mailto_template = t.render(c)
        mailto = [ e for e in mailto_template.split(",") if '@' in e ]

        return mailto

    def make_cc_list(self,context={}):
        t = Template(self.cc)
        c = Context(context)
        cc_template = t.render(c)
        cc = [ e for e in cc_template.split(",") if '@' in e ]

        return cc

    def make_bcc_list(self,context={}):
        t = Template(self.bcc)
        c = Context(context)
        bcc_template = t.render(c)
        bcc = [ e for e in bcc_template.split(",") if '@' in e ]

        return bcc

    def make_subject(self,context={}):
        t = Template(self.subject)
        c = Context(context)

        return t.render(c)

    def make_body(self,context={}):
        t = Template(self.body)
        c = Context(context)

        return t.render(c)

    def __unicode__(self):
        return self.name

class MailLog(models.Model):
    date_sent = models.DateTimeField(auto_now_add=True)
    from_host = models.CharField(max_length=256)
    recipient_emails = models.CharField(max_length=1024)
    reference_name = models.CharField(max_length=256)
    email_object=models.TextField()

    def __unicode__(self):
        return str(time.strftime(self.reference_name + '_%Y/%m/%d/%H:%M:%S'))
