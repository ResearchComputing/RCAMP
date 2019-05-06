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


class AllocationExpirationNotifierTestCase(SafeTestCase):

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

    def test_set_expiration_notice_field_when_notice_sent(self):
        pass

    def test_send_expiration_notice_for_expired_allocation(self):
        pass
