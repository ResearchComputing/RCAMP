from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from projects.models import Allocation
from projects.models import Project
from accounts.models import RcLdapUser



class Command(BaseCommand):
    help = 'Automatically manage membership for the scavenger project.'

    def add_arguments(self, parser):
        parser.add_argument('scavenger', type=str)

    def handle(self, *args, **options):
        # for poll_id in options['poll_id']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write('Successfully closed poll "%s"' % poll_id)
        now = timezone.now()
        last_year = now - relativedelta(years=1)

        scavenger_title = options['scavenger']
        try:
            scavenger = Project.objects.get(title=scavenger_title)
        except Project.DoesNotExist:
            raise CommandError('No Scavenger project found!')

        watch_list = []
        # Remove inviable users
        for user in scavenger.collaborators:
            # Was this user created more than one year ago?

            # If so, is this user in a valid project?

        # Add viable users
