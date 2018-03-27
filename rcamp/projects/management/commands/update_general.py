from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import datetime

from accounts.models import RcLdapUser
from projects.models import Project
from projects.models import Allocation



class Command(BaseCommand):
    help = 'Updates scavenger membership.'

    def handle(self, *args, **options):
        now = timezone.now()
        active_allocations = Allocation.objects.filter(
            start_date__lte=now,
            end_date__gte=now
        )

        try:
            ucb_general = Project.objects.get(title='ucb-general')
        except Project.DoesNotExist:
            ucb_general = None

        try:
            csu_general = Project.objects.get(title='csu-general')
        except Project.DoesNotExist:
            csu_general = None

        eligible_users = []
        for allocation in active_allocations:
            eligible_users += allocation.project.collaborators
            eligible_users += allocation.project.managers
        eligible_users = set(eligible_users)

        for username in eligible_users:
            try:
                user = RcLdapUser.objects.get(username=username)
                if csu_general and (user.organization.lower() == 'ou=csu'):
                    csu_general.collaborators.append(user.username)
                elif ucb_general and (user.organization.lower() == 'ou=ucb'):
                    ucb_general.collaborators.append(user.username)
            except RcLdapUser.DoesNotExist:
                continue

        if ucb_general:
            ucb_general.save()
        if csu_general:
            csu_general.save()

        self.stdout.write('Added {count} users to scavenger.'.format(count=len(eligible_users)))
