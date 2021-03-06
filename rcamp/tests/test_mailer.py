from django.test import TestCase
from django.test import override_settings
import copy


from mailer.models import MailNotifier
from mailer.models import MailLog
from mailer import receivers
from mailer.signals import *


# Ensure that the events exposed as choices for the
# data model match expectations
class EventChoicesTestCase(TestCase):
    def test_correct_events_exposed(self):
        from mailer.models import EVENT_CHOICES as event_choices
        expected_choices = (
            ('account_created_from_request', 'account_created_from_request'),
            ('account_request_approved', 'account_request_approved'),
            ('account_request_received', 'account_request_received'),
            ('allocation_created_from_request', 'allocation_created_from_request'),
            ('allocation_expiring', 'allocation_expiring'),
            ('allocation_expired', 'allocation_expired'),
            ('allocation_request_created_by_user', 'allocation_request_created_by_user'),
            ('project_created_by_user', 'project_created_by_user'),
        )
        self.assertEqual(sorted(event_choices), sorted(expected_choices))

# This test case covers MailNotifier functionality.
class MailNotifierTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'username':'testuser',
            'email':'testuser@test.org',
        }
        self.mn_dict = {
            'name':'account_request_received',
            'event':'account_request_received',
            'from_address':'test@test.org',
            'mailto':'requestuser@test.org,{{ email }},,',
            'cc':'requestuser@test.org,{{ email }},,',
            'bcc':'requestuser@test.org,{{ email }},,',
            'subject':'Hi, {{ username }}!',
            'body':'You, {{ username }}, did it!!!!',
        }
        self.mn = MailNotifier.objects.create(**self.mn_dict)

    def test_make_body(self):
        body = self.mn.make_body(self.ctx)

        self.assertEqual(self.mn.body,'You, {{ username }}, did it!!!!')
        self.assertEqual(body,'You, testuser, did it!!!!')

        # Test with no context
        body = self.mn.make_body()
        self.assertEqual(body,'You, , did it!!!!')

    def test_make_subject(self):
        subj = self.mn.make_subject(self.ctx)

        self.assertEqual(self.mn.subject,'Hi, {{ username }}!')
        self.assertEqual(subj,'Hi, testuser!')

        # Test with no context
        subj = self.mn.make_subject()
        self.assertEqual(subj,'Hi, !')

    def test_make_mailto_list(self):
        mailto = self.mn.make_mailto_list(self.ctx)

        self.assertEqual(
            mailto,
            ['requestuser@test.org','testuser@test.org']
        )
        self.assertEqual(self.mn.mailto,'requestuser@test.org,{{ email }},,')

        # Test with no context
        mailto = self.mn.make_mailto_list()
        self.assertEqual(mailto,['requestuser@test.org'])

    def test_make_cc_list(self):
        cc = self.mn.make_cc_list(self.ctx)

        self.assertEqual(
            cc,
            ['requestuser@test.org','testuser@test.org']
        )
        self.assertEqual(self.mn.cc,'requestuser@test.org,{{ email }},,')

        # Test with no context
        cc = self.mn.make_cc_list()
        self.assertEqual(cc,['requestuser@test.org'])

    def test_make_bcc_list(self):
        bcc = self.mn.make_bcc_list(self.ctx)

        self.assertEqual(
            bcc,
            ['requestuser@test.org','testuser@test.org']
        )
        self.assertEqual(self.mn.bcc,'requestuser@test.org,{{ email }},,')

        # Test with no context
        bcc = self.mn.make_bcc_list()
        self.assertEqual(bcc,['requestuser@test.org'])

    def test_make_email(self):
        email = self.mn.make_email(self.ctx)

        import django.core.mail.message
        self.assertIsInstance(email,django.core.mail.message.EmailMessage)

        self.assertEqual(email.subject,'Hi, testuser!')
        self.assertEqual(email.body,'You, testuser, did it!!!!')
        self.assertEqual(email.from_email,'test@test.org')
        self.assertEqual(email.to,['requestuser@test.org','testuser@test.org'])
        self.assertEqual(email.cc,['requestuser@test.org','testuser@test.org'])
        self.assertEqual(email.bcc,['requestuser@test.org','testuser@test.org'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send(self):
        msg = self.mn.send(self.ctx)

        import django.core.mail.message
        self.assertIsInstance(msg,django.core.mail.message.SafeMIMEText)

        from django.core.mail import outbox
        self.assertEqual(len(outbox),1)

        ml = MailLog.objects.get()
        self.assertEqual(ml.recipient_emails,'requestuser@test.org,testuser@test.org')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_save_tpl_error(self):
        mn_error_dict = copy.deepcopy(self.mn_dict)
        mn_error_dict['body'] = '{% if this will break %}'

        self.assertRaises(
            ValueError,
            MailNotifier.objects.create,
            **mn_error_dict
        )

class ARReceivedTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'username':'testuser',
            'email':'testuser@test.org',
        }
        mn1_dict = {
            'name':'account_request_received',
            'event':'account_request_received',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ account_request.email }},,",
            'cc':"requestuser@test.org,{{ account_request.email }},,",
            'bcc':"requestuser@test.org,{{ account_request.email }},,",
            'subject':"Hi, {{ account_request.username }}!",
            'body':"You, {{ account_request.username }}, did it!!!!",
        }
        mn2_dict = {
            'name':'account_request_received2',
            'event':'account_request_received',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ account_request.email }},,",
            'cc':"requestuser@test.org,{{ account_request.email }},,",
            'bcc':"requestuser@test.org,{{ account_request.email }},,",
            'subject':"Hi, {{ account_request.username }}!",
            'body':"You, {{ account_request.username }}, did it!!!!",
        }
        self.mn1 = MailNotifier.objects.create(**mn1_dict)
        self.mn2 = MailNotifier.objects.create(**mn2_dict)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_account_requested_received(self):
        account_request_received.send(
            sender='AccountRequest',
            account_request=self.ctx
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox),2)
        self.assertEqual(
            outbox[0].body,
            self.mn1.make_body({'account_request':self.ctx})
        )
        self.assertEqual(
            outbox[1].body,
            self.mn2.make_body({'account_request':self.ctx})
        )

class ARApprovedTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'username':'testuser',
            'email':'testuser@test.org',
        }
        mn1_dict = {
            'name':'account_created_from_request',
            'event':'account_created_from_request',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ account.email }},,",
            'cc':"requestuser@test.org,{{ account.email }},,",
            'bcc':"requestuser@test.org,{{ account.email }},,",
            'subject':"Hi, {{ account.username }}!",
            'body':"You, {{ account.username }}, did it!!!!",
        }
        mn2_dict = {
            'name':'account_created_from_request2',
            'event':'account_created_from_request',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ account.email }},,",
            'cc':"requestuser@test.org,{{ account.email }},,",
            'bcc':"requestuser@test.org,{{ account.email }},,",
            'subject':"Hi, {{ account.username }}!",
            'body':"You, {{ account.username }}, did it!!!!",
        }
        self.mn1 = MailNotifier.objects.create(**mn1_dict)
        self.mn2 = MailNotifier.objects.create(**mn2_dict)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_account_requested_received(self):
        account_created_from_request.send(
            sender='RcLdapUser',
            account=self.ctx
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox),2)
        self.assertEqual(
            outbox[0].body,
            self.mn1.make_body({'account':self.ctx})
        )
        self.assertEqual(
            outbox[1].body,
            self.mn2.make_body({'account':self.ctx})
        )

class ProjectCreatedTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'project_id':'test1',
            'pi_emails':'testuser@test.org,testuser2@test.org',
        }
        mn1_dict = {
            'name':'project_created_by_user',
            'event':'project_created_by_user',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ project.pi_emails }},,",
            'cc':"requestuser@test.org,{{ project.pi_emails }},,",
            'bcc':"requestuser@test.org,{{ project.pi_emails }},,",
            'subject':"Hi, {{ project.project_id }} has been created!",
            'body':"Project id: {{ project.project_id }}.",
        }
        mn2_dict = {
            'name':'project_created_by_user2',
            'event':'project_created_by_user',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ project.pi_emails }},,",
            'cc':"requestuser@test.org,{{ project.pi_emails }},,",
            'bcc':"requestuser@test.org,{{ project.pi_emails }},,",
            'subject':"Hi, {{ project.project_id }} has been created!",
            'body':"Project id: {{ project.project_id }}.",
        }
        self.mn1 = MailNotifier.objects.create(**mn1_dict)
        self.mn2 = MailNotifier.objects.create(**mn2_dict)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_project_created_by_user(self):
        project_created_by_user.send(
            sender='Project',
            project=self.ctx
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox),2)
        self.assertEqual(
            outbox[0].body,
            self.mn1.make_body({'project':self.ctx})
        )
        self.assertEqual(
            outbox[1].body,
            self.mn2.make_body({'project':self.ctx})
        )

class AllocReqReceivedTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'username':'testuser',
            'email':'testuser@test.org',
        }
        mn1_dict = {
            'name':'allocation_request_created_by_user',
            'event':'allocation_request_created_by_user',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ allocation_request.email }},,",
            'cc':"requestuser@test.org,{{ allocation_request.email }},,",
            'bcc':"requestuser@test.org,{{ allocation_request.email }},,",
            'subject':"Hi, {{ allocation_request.username }}!",
            'body':"You, {{ allocation_request.username }}, did it!!!!",
        }
        mn2_dict = {
            'name':'allocation_request_created_by_user2',
            'event':'allocation_request_created_by_user',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ allocation_request.email }},,",
            'cc':"requestuser@test.org,{{ allocation_request.email }},,",
            'bcc':"requestuser@test.org,{{ allocation_request.email }},,",
            'subject':"Hi, {{ allocation_request.username }}!",
            'body':"You, {{ allocation_request.username }}, did it!!!!",
        }
        self.mn1 = MailNotifier.objects.create(**mn1_dict)
        self.mn2 = MailNotifier.objects.create(**mn2_dict)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_allocation_request_received(self):
        allocation_request_created_by_user.send(
            sender='AllocationRequest',
            allocation_request=self.ctx,
            requester=self.ctx
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox),2)
        self.assertEqual(
            outbox[0].body,
            self.mn1.make_body({'allocation_request':self.ctx})
        )
        self.assertEqual(
            outbox[1].body,
            self.mn2.make_body({'allocation_request':self.ctx})
        )

class ARApprovedTestCase(TestCase):
    def setUp(self):
        self.ctx = {
            'username':'testuser',
            'email':'testuser@test.org',
        }
        mn1_dict = {
            'name':'allocation_created_from_request',
            'event':'allocation_created_from_request',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ allocation.email }},,",
            'cc':"requestuser@test.org,{{ allocation.email }},,",
            'bcc':"requestuser@test.org,{{ allocation.email }},,",
            'subject':"Hi, {{ allocation.username }}!",
            'body':"You, {{ allocation.username }}, did it!!!!",
        }
        mn2_dict = {
            'name':'allocation_created_from_request2',
            'event':'allocation_created_from_request',
            'from_address':'test@test.org',
            'mailto':"requestuser@test.org,{{ allocation.email }},,",
            'cc':"requestuser@test.org,{{ allocation.email }},,",
            'bcc':"requestuser@test.org,{{ allocation.email }},,",
            'subject':"Hi, {{ allocation.username }}!",
            'body':"You, {{ allocation.username }}, did it!!!!",
        }
        self.mn1 = MailNotifier.objects.create(**mn1_dict)
        self.mn2 = MailNotifier.objects.create(**mn2_dict)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_allocation_requested_received(self):
        allocation_created_from_request.send(
            sender='Allocation',
            allocation=self.ctx
        )

        from django.core.mail import outbox
        self.assertEqual(len(outbox),2)
        self.assertEqual(
            outbox[0].body,
            self.mn1.make_body({'allocation':self.ctx})
        )
        self.assertEqual(
            outbox[1].body,
            self.mn2.make_body({'allocation':self.ctx})
        )
