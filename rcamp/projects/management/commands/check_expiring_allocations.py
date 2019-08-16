import datetime
import logging
import sys
import os
import django

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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rcamp.settings")
django.setup()

logger = logging.getLogger('management_commands')


class Command(BaseCommand):
    help = 'Send notifications for allocations that have expired or are soon to expire'

    def add_arguments(self, parser):
        parser.add_argument('--notice-intervals',
            type=str,
            nargs='?',
            const='30,14',
            default='',
            help="Comma separated list of intervals in days at which owners of \
                expriring allocations will be notified. default='30,14' \
                '' if argument not specified"
        )
        parser.add_argument('--quiet',
            action='store_const',
            const=True,
            help="Suppress log messages."
        )

    def handle(self, *args, **options):
        self.quiet = options.get('quiet', False)
        interval_argument = options.get('notice_intervals')
        intervals = self._get_intervals_from_argument(interval_argument)

        for interval in intervals:
            upcoming_expiration_notifier = UpcomingExpirationNotifier(self.quiet, interval)
            upcoming_expiration_notifier.send_upcoming_expiration_notices()

        expiration_notifier = ExpirationNotifier(self.quiet)
        expiration_notifier.send_expiration_notices()

    def _get_intervals_from_argument(self, interval_argument):

        intervals = []
        interval_arg_slices = [interval_arg_slice.strip() for interval_arg_slice in interval_argument.split(',') if interval_arg_slice]
        for interval_arg_slice in interval_arg_slices:
            interval = int(interval_arg_slice)
            if interval < 1:
                raise ValueError("An interval must be positive integer > 0")

            intervals.append(interval)

        return intervals


class ExpirationNotifier():
    """Manages notifications for expired allocations."""

    def __init__(self, quiet):
        self.quiet = quiet

    def get_expired_allocations_with_no_sent_notification(self):
        expired_allocations = Allocation.objects.filter(
            end_date__lte=timezone.now(),
            expiration_notice_sent=False
        )
        return expired_allocations

    def send_expiration_notices(self):
        expired_allocations = self.get_expired_allocations_with_no_sent_notification()
        with open('/opt/logs/management_commands', 'a') as f:
            f.write("Sending expiration notices, f.write")
        #sys.stdout.write("Sending expiration notices, sys")
        logger.info("Sending expiration notices")
        for allocation in expired_allocations:
            try:
                signal_return = allocation_expired.send(sender=allocation.__class__, allocation=allocation)
                log_message = """Expired:
                    signal_return={signal_return}
                    end_date={end_date}
                    notice_sent={notice_sent}""".format(signal_return=signal_return,
                                                        end_date=allocation.end_date,
                                                        notice_sent=allocation.expiration_notice_sent)
                with open('/opt/logs/management_commands', 'a') as f:
                    for line in log_message:
                        f.write(line)
                logger.info(log_message)
                allocation.expiration_notice_sent = True
                allocation.save()
            except Exception as e:
                with open('/opt/logs/management_commands', 'a') as f:
                    f.write("Expiration notices error, f.write")
                logger.warn('Expiration notices error')
                logger.warn(e)


class UpcomingExpirationNotifier():
    """Manages notifications for soon-to-expire allocations."""

    def __init__(self, quiet, interval):
        self.quiet = quiet
        self.interval = interval

    def get_expiring_allocations_for_interval(self):
        expiration_date = timezone.now() + datetime.timedelta(days=self.interval)
        expiring_allocations = Allocation.objects.filter(end_date=expiration_date)
        return expiring_allocations

    def send_upcoming_expiration_notices(self):
        expiring_allocations = self.get_expiring_allocations_for_interval()
        with open('/opt/logs/management_commands', 'a') as f:
            f.write("Sending upcoming expiration notices, f.write")
        logger.info("Sending upcoming expiration notices")
        for allocation in expiring_allocations:
            try:
                signal_return = allocation_expiring.send(sender=allocation.__class__, allocation=allocation)
                log_message = """Expiring interval={interval}:
                    signal_return={signal_return}
                    end_date={end_date}
                    notice_sent={notice_sent}""".format(interval=self.interval,
                                                        signal_return=signal_return,
                                                        end_date=allocation.end_date,
                                                        notice_sent=allocation.expiration_notice_sent)
                with open('/opt/logs/management_commands', 'a') as f:
                    for line in log_message:
                        f.write(line)
                logger.info(log_message)
            except Exception as e:
                with open('/opt/logs/management_commands', 'a') as f:
                    f.write("Upcoming expiration notices error, f.write")
                logger.warn('Upcoming expiration notices error')
                logger.warn(e)
