import sys
import os
import re
from django.conf import settings
from datetime import datetime
import logging
from ldap import initialize, SCOPE_SUBTREE
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

AUTH_LDAP_BIND_DN = str(settings.LDAPCONFS['rcldap']['bind_dn'])
AUTH_LDAP_BIND_PASSWORD = str(settings.LDAPCONFS['rcldap']['bind_pw'])
LDAP_SERVER = str(settings.LDAPCONFS['rcldap']['server'])

# Currently only checking for AMC accounts
affiliation_map = {
    "cuanschutz": "amc",
}
usernames = {}

def get_ldap_users():
    conn = initialize(LDAP_SERVER)
    conn.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)

    filters = ['(homeDirectory=*)', '(objectClass=posixAccount)']
    search_filter = '(&{0})'.format(''.join(filters))
    search_attributes = ('homeDirectory', 'uidNumber', 'gidNumber', 'uid', 'givenName', 'sn', 'mail', 'createTimestamp')
    #XSEDE_PEOPLE_OU = "ou=XSEDE,ou=people,dc=rc,dc=int,dc=colorado,dc=edu"
    AMC_PEOPLE_OU = "ou=AMC,ou=people,dc=rc,dc=int,dc=colorado,dc=edu"
    #xsede_users = conn.search_s(XSEDE_PEOPLE_OU, SCOPE_SUBTREE, search_filter, search_attributes)
    amc_users = conn.search_s(AMC_PEOPLE_OU, SCOPE_SUBTREE, search_filter, search_attributes)
    all_users = amc_users
    
    return all_users
def is_curc_format(s):
    pattern = r'^[a-z]{4}\d{4}_[a-z]{3}$'
    return bool(re.match(pattern, s))

def username_previously_generated(user):
    global usernames
    username_exists = False
    uid = user['uid'][0].decode().lower()
    if is_curc_format(uid):
        usernames[uid] = user
        username_exists = True
    return username_exists

def populate_usernames():
    global usernames
    usernames = {}
    users = get_ldap_users()
    for user in users:
        user = user[1]
        username_created = username_previously_generated(user)
        email = user['mail'][0].decode().lower()
        index = 1
        for key in affiliation_map.keys():
            if key in email:
                while(username_created == False):
                    first = user['givenName'][0].decode().lower()
                    last = user['sn'][0].decode().lower()
                    possible_username = first[:2] + last[:2] + str(index).zfill(4) + "_" + affiliation_map[key]
                    if possible_username in usernames.keys():
                        other_user = usernames[possible_username]
                        d1 = datetime.strptime(other_user['createTimestamp'][0].decode(), "%Y%m%d%H%M%SZ")
                        d2 = datetime.strptime(user['createTimestamp'][0].decode(), "%Y%m%d%H%M%SZ")
                        if d1 <= d2:
                            index += 1
                        else:
                            usernames[possible_username] = user
                            user = other_user
                            index += 1
                    else:
                        usernames[possible_username] = user
                        username_created = True

def check_ldap(email):
    conn = initialize(LDAP_SERVER)
    conn.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)

    filters = ['(homeDirectory=*)', '(objectClass=posixAccount)', '(mail='+email+')']
    search_filter = '(&{0})'.format(''.join(filters))
    search_attributes = ('homeDirectory', 'uidNumber', 'gidNumber', 'uid', 'givenName', 'sn', 'mail', 'createTimestamp')
    AMC_PEOPLE_OU = "ou=AMC,ou=people,dc=rc,dc=int,dc=colorado,dc=edu"
    ldap_user = conn.search_s(AMC_PEOPLE_OU, SCOPE_SUBTREE, search_filter, search_attributes)
    
    return ldap_user

def generate_curc_uid(first, last, email, organization):
    global usernames
    logger = logging.getLogger('rcamp.lib.generate_usernames')
    populate_usernames()
    user = check_ldap(email)
    fila = first[:2].lower() + last[:2].lower()
    username = None
    if user is None or len(user) < 1:
        logger.info("No user with email exists, lets get them a username")
        user_id_numbers = []
        for curc_uid in usernames.keys():
            if fila.lower() in curc_uid and organization in curc_uid:
                logger.info("user id number")
                logger.info(curc_uid)
                logger.info(int(curc_uid[4:8]))
                user_id_numbers.append(int(curc_uid[4:8])) # this will grab the number from fila####_org
        logger.info(user_id_numbers)
        id_number = get_available_id(user_id_numbers)
        username = fila + str(id_number).zfill(4) + "_" + organization
        logger.info(username)
        logger.info(id_number)

    else:
        logger.info("The user already exists")
    
    return username

def get_available_id(user_id_numbers):
    id_number = 1
    if len(user_id_numbers) > 0:
        user_id_numbers.sort()
        id_number = user_id_numbers[-1] + 1        
    return id_number