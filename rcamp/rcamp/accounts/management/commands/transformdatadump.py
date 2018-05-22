from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import datetime
import sys
import os
import json
import copy

from accounts.models import User


class Command(BaseCommand):
    help = """Transforms a data dump from pre-v17.12 RCAMP to a version that v17.12 can load. To generate a compatible dump, run the following command:\n\npython manage.py dumpdata --output=old-version-dump.json --indent=4 --exclude=contenttypes --exclude=sessions --exclude=auth --exclude=admin\n"""

    def add_arguments(self, parser):
        parser.add_argument('input_file',
            type=str,
            help="Name of the JSON data dump file to transform."
        )
        parser.add_argument('--output',
            type=str,
            help="Name of the transformed JSON file."
        )

    def transform_user_list_to_pk(self,user_list,user_pk_lookup):
        pk_list = []
        for username in user_list.split(','):
            if not username:
                continue
            try:
                pk = user_pk_lookup[username]
                pk_list.append(pk)
            except KeyError:
                self.stderr.write('User {username} not found in accounts.user! Ignoring...'.format(username=username))
                continue
        return pk_list

    def handle(self, *args, **options):
        dump_filename = options.get('input_file')
        transformed_filename = options.get('output','transformed-data.json')
        original_data = json.load(open(dump_filename))

        # Sync users should have been run already. If it hasn't bail out.
        auth_users = User.objects.all()
        if auth_users.count() < 2:
            self.stderr.write('Fewer than 2 users found! Did you run syncldapusers already?')
            sys.exit(1)

        user_pk_lookup = dict([(user.username,user.pk) for user in auth_users])
        transformed_data = copy.deepcopy(original_data)

        for entry in transformed_data:
            # Remove projects field from account requests
            if entry['model'] == 'accounts.accountrequest':
                del entry['fields']['projects']

            # Iterate over projects, replacing string references with accounts.User pks
            elif entry['model'] == 'projects.project':
                collaborators_old = entry['fields']['collaborators']
                managers_old = entry['fields']['managers']
                collaborators_transformed = self.transform_user_list_to_pk(collaborators_old,user_pk_lookup)
                managers_transformed = self.transform_user_list_to_pk(managers_old,user_pk_lookup)
                entry['fields']['collaborators'] = collaborators_transformed
                entry['fields']['managers'] = managers_transformed

            # Iterate over allocation requests and replace requester strings with pk reference
            elif entry['model'] == 'projects.allocationrequest':
                requester_old = entry['fields']['requester']
                requester_pk = user_pk_lookup.get(requester_old,None)
                entry['fields']['requester'] = requester_pk

        # Write out transformed data to file
        with open(transformed_filename, 'w') as outfile:
            json.dump(transformed_data, outfile, indent=4)

        self.stdout.write('Wrote transformed data dump to {filename}!'.format(filename=transformed_filename))
