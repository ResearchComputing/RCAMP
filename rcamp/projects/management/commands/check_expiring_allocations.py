import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from projects.models import (
    Project,
    Allocation,
)

from mailer.models import (
    MailLog,
    MailNotifier,
)

from mailer.signals import (
    allocation_expiring,
    allocation_expired,
)


class Command(BaseCommand):
    help = 'Send notifications for allocations that have expired or are soon to expire'

    def add_arguments(self, parser):
        parser.add_argument('--notice-intervals',
            action='store_const',
            const=True,
            default='90,30,14',
            help="Comma separated list of intervals in days at which owners of \
                expriring allocations will be notified. default='90,30,14'"
        )

    def handle(self, *args, **options):

        intervals = self._get_intervals_from_argument()

        for interval in intervals:
            upcoming_expiration_notifier = UpcomingExpirationNotifier(interval)
            upcoming_expiration_notifier.send_upcoming_expiration_notices()

        expiration_notifier = ExpirationNotifier()
        expiration_notifier.send_expiration_notices()

    def _get_intervals_from_argument(self):
        interval_argument = options.get('notice-intervals',False)

        intervals = []
        for interval_arg_slice in interval_argument.split(','):
            interval = int(interval_arg_slice.strip())
            if interval < 1:
                raise ValueError("An interval must be positive integer > 0")

            intervals.append(interval)

        return intervals


class ExpirationNotifier():
    """Manages notifications for expired allocations."""

    def get_expired_allocations_with_no_sent_notification(self):
        expired_allocations = Allocation.objects.filter(
            end_date__lte=timezone.now(),
            expiration_notice_sent=False
        )
        return expired_allocations

    def send_expiration_notices(self):
        expired_allocations = self.get_expired_allocations_with_no_sent_notification()
        for allocation in expired_allocations:
            allocation_expired.send(sender=allocation.__class__, allocation=allocation)
            allocation.expiration_notice_sent = True
            allocation.save()


class UpcomingExpirationNotifier():
    """Manages notifications for soon-to-expire allocations."""

    def __init__(self, interval):
        self.interval = interval

    def get_expiring_allocations_for_interval(self):
        expiration_date = timezone.now() + datetime.timedelta(days=self.interval)
        expiring_allocations = Allocation.objects.filter(end_date=expiration_date)
        return expiring_allocations

    def send_upcoming_expiration_notices(self):
        expiring_allocations = self.get_expiring_allocations_for_interval()
        for allocation in expiring_allocations:
            allocation_expiring.send(sender=allocation.__class__, allocation=allocation)
