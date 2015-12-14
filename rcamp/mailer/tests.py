from django.test import TestCase
from django.test import override_settings

from mailer.models import MailNotifier
from mailer.models import MailLog


# Ensure that the events exposed as choices for the
# data model match expectations
class EventChoicesTestCase(TestCase):
    def test_correct_events_exposed(self):
        from mailer.models import EVENT_CHOICES as event_choices
        expected_choices = (
            ('account_created_from_request', 'account_created_from_request'),
            ('account_request_received', 'account_request_received'),
        )
        self.assertEquals(event_choices,expected_choices)

# This test case covers MailNotifier functionality.
class MailNotifierTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'username':'testuser',
            'email':'testuser@test.org',
        }
        mn_dict = {
            'name':'account_request_received',
            'event':'account_request_received',
            'from_address':'test@test.org',
            'mailto':'requestuser@test.org,{{ email }},,',
            'cc':'requestuser@test.org,{{ email }},,',
            'bcc':'requestuser@test.org,{{ email }},,',
            'subject':'Hi, {{ username }}!',
            'body':'You, {{ username }}, did it!!!!',
        }
        self.mn = MailNotifier.objects.create(**mn_dict)
    
    def test_make_body(self):
        body = self.mn.make_body(self.ctx)
        
        self.assertEquals(self.mn.body,'You, {{ username }}, did it!!!!')
        self.assertEquals(body,'You, testuser, did it!!!!')
        
        # Test with no context
        body = self.mn.make_body()
        self.assertEquals(body,'You, , did it!!!!')
    
    def test_make_subject(self):
        subj = self.mn.make_subject(self.ctx)
        
        self.assertEquals(self.mn.subject,'Hi, {{ username }}!')
        self.assertEquals(subj,'Hi, testuser!')
        
        # Test with no context
        subj = self.mn.make_subject()
        self.assertEquals(subj,'Hi, !')
    
    def test_make_mailto_list(self):
        mailto = self.mn.make_mailto_list(self.ctx)
        
        self.assertEquals(
            mailto,
            ['requestuser@test.org','testuser@test.org']
        )
        self.assertEquals(self.mn.mailto,'requestuser@test.org,{{ email }},,')
        
        # Test with no context
        mailto = self.mn.make_mailto_list()
        self.assertEquals(mailto,['requestuser@test.org'])
    
    def test_make_cc_list(self):
        cc = self.mn.make_cc_list(self.ctx)
        
        self.assertEquals(
            cc,
            ['requestuser@test.org','testuser@test.org']
        )
        self.assertEquals(self.mn.cc,'requestuser@test.org,{{ email }},,')
        
        # Test with no context
        cc = self.mn.make_cc_list()
        self.assertEquals(cc,['requestuser@test.org'])
    
    def test_make_bcc_list(self):
        bcc = self.mn.make_bcc_list(self.ctx)
        
        self.assertEquals(
            bcc,
            ['requestuser@test.org','testuser@test.org']
        )
        self.assertEquals(self.mn.bcc,'requestuser@test.org,{{ email }},,')
        
        # Test with no context
        bcc = self.mn.make_bcc_list()
        self.assertEquals(bcc,['requestuser@test.org'])
    
    def test_make_email(self):
        email = self.mn.make_email(self.ctx)
        
        import django.core.mail.message
        self.assertIsInstance(email,django.core.mail.message.EmailMessage)
        
        self.assertEquals(email.subject,'Hi, testuser!')
        self.assertEquals(email.body,'You, testuser, did it!!!!')
        self.assertEquals(email.from_email,'test@test.org')
        self.assertEquals(email.to,['requestuser@test.org','testuser@test.org'])
        self.assertEquals(email.cc,['requestuser@test.org','testuser@test.org'])
        self.assertEquals(email.bcc,['requestuser@test.org','testuser@test.org'])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send(self):
        msg = self.mn.send(self.ctx)
        
        import django.core.mail.message
        self.assertIsInstance(msg,django.core.mail.message.SafeMIMEText)
        
        from django.core.mail import outbox
        self.assertEquals(len(outbox),1)
        
        ml = MailLog.objects.get()
        self.assertEquals(ml.recipient_emails,'requestuser@test.org,testuser@test.org')
