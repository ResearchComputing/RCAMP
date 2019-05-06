from django.test import override_settings
from django.conf import settings
import mock
import datetime
import pytz

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from projects.models import (
    Project,
    Allocation,
)
from projects.management.commands.check_expiring_allocations import (
    Command,
    ExpirationNotifier,
    UpcomingExpirationNotifier,
)
from tests.utilities.utils import (
    SafeTestCase,
)


class ExpirationNotifierTestCase(SafeTestCase):

    def setUp(self):
        self.proj_dict = {
            'project_id': 'ucb7',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'organization':'ucb',
        }
        self.proj = Project.objects.create(**self.proj_dict)

    def test_only_return_unnotified_expired_allocations(self):

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,02,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)

        alloc_dict_not_notified = {
            'project': self.proj,
            'allocation_id': 'ucb7_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
            'expiration_notice_sent': False
        }
        alloc_not_notified = Allocation.objects.create(**alloc_dict_not_notified)

        alloc_dict_notified = {
            'project': self.proj,
            'allocation_id': 'ucb6_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
            'expiration_notice_sent': True
        }
        alloc_notified = Allocation.objects.create(**alloc_dict_notified)

        expiration_notifier = ExpirationNotifier()
        actual_allocations = expiration_notifier.get_expired_allocations_with_no_sent_notification()
        expected_query_set = [alloc_not_notified]

        self.assertEqual(expected_query_set, list(actual_allocations))

    def test_only_return_allocations_with_passed_expiration_date(self):

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate_in_past = datetime.datetime(2017,02,02)
        edate_in_past_tz = pytz.timezone('America/Denver').localize(edate_in_past)
        edate_in_future = datetime.datetime(2019,02,02)
        edate_in_future_tz = pytz.timezone('America/Denver').localize(edate_in_future)
        current_date_for_test = datetime.datetime(2018,02,02)
        current_date_for_test_tz = pytz.timezone('America/Denver').localize(current_date_for_test)

        with mock.patch('django.utils.timezone.now', return_value=current_date_for_test):

            alloc_dict_end_date_passed = {
                'project': self.proj,
                'allocation_id': 'ucb7_summit2',
                'amount': '50000',
                'start_date': sdate_tz,
                'end_date': edate_in_past_tz,
                'expiration_notice_sent': False
            }
            alloc_end_date_passed = Allocation.objects.create(**alloc_dict_end_date_passed)

            alloc_dict_end_date_future = {
                'project': self.proj,
                'allocation_id': 'ucb6_summit2',
                'amount': '50000',
                'start_date': sdate_tz,
                'end_date': edate_in_future_tz,
                'expiration_notice_sent': False
            }
            alloc_end_date_future = Allocation.objects.create(**alloc_dict_end_date_future)

            expiration_notifier = ExpirationNotifier()
            actual_allocations = expiration_notifier.get_expired_allocations_with_no_sent_notification()
            expected_query_set = [alloc_end_date_passed]

            self.assertEqual(expected_query_set, list(actual_allocations))

    def test_send_expiration_notice_for_expired_allocation(self):

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,02,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)

        alloc_dict_not_notified = {
            'project': self.proj,
            'allocation_id': 'ucb7_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
            'expiration_notice_sent': False
        }
        alloc_not_notified = Allocation.objects.create(**alloc_dict_not_notified)

        with mock.patch('mailer.signals.allocation_expired.send') as mock_send:
            expiration_notifier = ExpirationNotifier()
            expiration_notifier.send_expiration_notices()

            self.assertEqual(mock_send.call_count, 1)

    def test_expiration_notice_field_set_when_notice_sent(self):
        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate = datetime.datetime(2017,02,02)
        edate_tz = pytz.timezone('America/Denver').localize(edate)

        alloc_dict_not_notified = {
            'project': self.proj,
            'allocation_id': 'ucb7_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_tz,
            'expiration_notice_sent': False
        }
        alloc_not_notified = Allocation.objects.create(**alloc_dict_not_notified)

        with mock.patch('mailer.signals.allocation_expired.send'):
            expiration_notifier = ExpirationNotifier()
            expiration_notifier.send_expiration_notices()
            actual_allocation_object = Allocation.objects.get(allocation_id='ucb7_summit2')

            self.assertEqual(True, actual_allocation_object.expiration_notice_sent)


class UpcomingExpirationNotifierTestCase(SafeTestCase):

    def setUp(self):
        self.proj_dict = {
            'project_id': 'ucb7',
            'title': 'Test Project',
            'description': 'A test project',
            'pi_emails': ['testuser@test.org','cuuser@cu.edu'],
            'organization':'ucb',
        }
        self.proj = Project.objects.create(**self.proj_dict)

    def test_return_soon_to_expire_allocations_at_interval_date(self):

        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        edate_expired = datetime.datetime(2017,02,02)
        edate_expired_tz = pytz.timezone('America/Denver').localize(edate_expired)
        edate_far_in_future = datetime.datetime(2030,02,02)
        edate_far_in_future_tz = pytz.timezone('America/Denver').localize(edate_far_in_future)
        edate_notice_needed = datetime.datetime(2018,02,21)
        edate_notice_needed_tz = pytz.timezone('America/Denver').localize(edate_notice_needed)
        current_date_for_test = datetime.datetime(2018,02,01)
        current_date_for_test_tz = pytz.timezone('America/Denver').localize(current_date_for_test)

        alloc_dict_notification_needed = {
            'project': self.proj,
            'allocation_id': 'ucb7_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_notice_needed_tz,
            'expiration_notice_sent': False
        }
        alloc_notification_needed = Allocation.objects.create(**alloc_dict_notification_needed)

        # Expired allocations don't need upcoming notification
        alloc_dict_expired = {
            'project': self.proj,
            'allocation_id': 'ucb6_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_expired_tz,
            'expiration_notice_sent': True
        }
        alloc_expired = Allocation.objects.create(**alloc_dict_expired)

        # Notification date in future
        alloc_dict_no_notification = {
            'project': self.proj,
            'allocation_id': 'ucb8_summit3',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_far_in_future_tz,
            'expiration_notice_sent': False
        }
        alloc_no_notification = Allocation.objects.create(**alloc_dict_no_notification)

        with mock.patch('django.utils.timezone.now', return_value=current_date_for_test):
            notification_interval = 20
            upcoming_expiration_notifier = UpcomingExpirationNotifier(notification_interval)
            actual_allocations = upcoming_expiration_notifier.get_expiring_allocations_for_interval()
            expected_query_set = [alloc_notification_needed]

            self.assertEqual(expected_query_set, list(actual_allocations))

    def test_send_upcoming_expiration_notice(self):
        
        sdate = datetime.datetime(2016,02,02)
        sdate_tz = pytz.timezone('America/Denver').localize(sdate)
        current_date_for_test = datetime.datetime(2018,02,01)
        current_date_for_test_tz = pytz.timezone('America/Denver').localize(current_date_for_test)
        edate_notice_needed = datetime.datetime(2018,02,21)
        edate_notice_needed_tz = pytz.timezone('America/Denver').localize(edate_notice_needed)

        alloc_dict_notification_needed = {
            'project': self.proj,
            'allocation_id': 'ucb7_summit2',
            'amount': '50000',
            'start_date': sdate_tz,
            'end_date': edate_notice_needed_tz,
            'expiration_notice_sent': False
        }
        alloc_notification_needed = Allocation.objects.create(**alloc_dict_notification_needed)

        with mock.patch('mailer.signals.allocation_expiring.send') as mock_send, \
                mock.patch('django.utils.timezone.now', return_value=current_date_for_test):
            notification_interval = 20
            upcoming_expiration_notifier = UpcomingExpirationNotifier(notification_interval)
            upcoming_expiration_notifier.send_upcoming_expiration_notices()

            self.assertEqual(mock_send.call_count, 1)
