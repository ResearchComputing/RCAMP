from django.conf import settings
import mock
from lib.ldap_utils import (
    get_suffixed_username,
    get_ldap_username_and_org
)
from lib.test.utils import SafeTestCase


class LdapUtilsTestCase(SafeTestCase):
    def test_get_suffixed_username(self):
        organization_info =  {
            'ucb': {
                'long_name': 'University of Colorado Boulder',
                'suffix': None
            },
            'csu': {
                'long_name': 'Colorado State University',
                'suffix': 'colostate.edu'
            }
        }
        with self.settings(ORGANIZATION_INFO=organization_info):
            username = 'testuser'
            organization = 'ucb'
            suffixed_username = get_suffixed_username(username,organization)
            self.assertEquals(suffixed_username,'testuser')

            username = 'testuser'
            organization = 'csu'
            suffixed_username = get_suffixed_username(username,organization)
            self.assertEquals(suffixed_username,'testuser@colostate.edu')

            username = 'testuser'
            organization = 'invalid'
            suffixed_username = get_suffixed_username(username,organization)
            self.assertEquals(suffixed_username,'testuser')

    def test_get_ldap_username_and_org(self):
        organization_info =  {
            'ucb': {
                'long_name': 'University of Colorado Boulder',
                'suffix': None
            },
            'csu': {
                'long_name': 'Colorado State University',
                'suffix': 'colostate.edu'
            }
        }
        with self.settings(ORGANIZATION_INFO=organization_info):
            suffixed_username = 'testuser'
            username, organization = get_ldap_username_and_org(suffixed_username)
            self.assertEquals(username,'testuser')
            self.assertEquals(organization,'ucb')

            suffixed_username = 'testuser@colostate.edu'
            username, organization = get_ldap_username_and_org(suffixed_username)
            self.assertEquals(username,'testuser')
            self.assertEquals(organization,'csu')

            suffixed_username = 'testuser@invalid'
            username, organization = get_ldap_username_and_org(suffixed_username)
            self.assertEquals(username,'testuser')
            self.assertEquals(organization,'ucb')

            # Make sure the admin won't tank if something strange happens
            # with suffixes.
            suffixed_username = 'testuser@oops@colostate.edu'
            username, organization = get_ldap_username_and_org(suffixed_username)
            self.assertEquals(username,'testuser@oops')
            self.assertEquals(organization,'csu')
