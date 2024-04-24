from faker import Faker
from datetime import datetime, timedelta, tzinfo
from random import randrange
fake = Faker()


class UTC(tzinfo):
    def __init__(self):
        super(UTC, self).__init__()

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

some_tz = UTC()


def now_with_tz():
    return datetime.now(some_tz).isoformat()


def venue_based_event(location=1):
    base_name = fake.words()
    slug = '-'.join(base_name)
    ev_name = ' '.join(base_name)
    ticket_types = [
        {
            'notification_users': [],
            'shipping_type': ['2'],
            'visibility': 1,
            'ticket_transfer_enabled': True,
            'sort_order': 0,
            'name': ' '.join(fake.words()),
            'inventory': 50000,
            'price': 1 + x
        } for x in range(1, randrange(2, 10))
    ]

    return {
        'is_published_for_sellers': True,
        'is_published': True,
        'tickettype_set': ticket_types,
        'visibility': 1,
        'message': None,
        'daily_report_emails': [],
        'starts_on': (datetime.now(some_tz) + timedelta(days=7)).isoformat(),
        'ends_on': (datetime.now(some_tz) + timedelta(days=14)).isoformat(),
        'starts_on_timezone': (datetime.now(some_tz) + timedelta(days=7)).isoformat(),
        'starts_on_time_timezone': (datetime.now(some_tz) + timedelta(days=7)).isoformat(),
        'ends_on_timezone': (datetime.now(some_tz) + timedelta(days=14)).isoformat(),
        'ends_on_time_timezone': (datetime.now(some_tz) + timedelta(days=14)).isoformat(),
        'timezone': 'America/Edmonton',
        'name': ev_name,
        'description': '<p>%s</p>' % fake.paragraph(),
        'tags': [fake.word()],
        'location': location
    }


def auth_user():
    return {
        'email': fake.email(),
        'password': 'password',
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'password1': 'password',
        'password2': 'password'
    }

def location_data(venue):
    return {
        'city': fake.city(),
        'name': ' '.join(fake.words()),
        'position': '51.0486151,-114.0708459',
        'street_name': fake.street_address(),
        'province': fake.state(),
        'postal_code': fake.postalcode(),
        'venue': venue,
    }

def user_based_venue(email=None):
    email = fake.safe_email() if email is None else email
    return {
        'modules_enabled': [
            '1',
            '2',
            '3',
            '4'
        ],
        'email': fake.safe_email(),
        'timezone': 'America/Edmonton',
        'category': 1,
        'name': fake.company(),
        'phone_number': fake.phone_number(),
        'street_name': fake.street_address(),
        'country': 'Canada',
        'province': fake.state(),
        'city': fake.city(),
        'postal_code': fake.postalcode(),
        'currency': 'CAD',
        'position': '53.4967195, -113.4914018'
    }


def user_based_basket(tix_type=1, tix_quantity=1, tt_location_permissions=None):
    if tt_location_permissions is None:
        tt_location_permissions = []
    return {
        'item_groups': [
            {
                'item_type': 'ticket',
                'type': tix_type,
                'tt_seat_permissions': [],
                'tt_location_permissions': tt_location_permissions,
                'scan_codes': [],
                'quantity': tix_quantity,
            }
        ],
        'purchase_source_platform': 'psp_web',
        'sold_by_venue': None,
    }

def user_based_membership_basket(level=1, quantity=1, tt_location_permissions=None):
    if tt_location_permissions is None:
        tt_location_permissions = []
    return {
        'item_groups': [
            {
                'item_type': 'membership',
                'membership_level': level,
                'tt_seat_permissions': [],
                'tt_location_permissions': tt_location_permissions,
                'scan_codes': [],
                'quantity': quantity,
            }
        ],
        'purchase_source_platform': 'psp_web',
        'sold_by_venue': None,
    }


def user_based_cc_basket_purchase(basket_id):
    return {
        'payment_type': 2,
        'basket': basket_id,
        'id': basket_id,
        'billing_address': {
            'street_address': fake.street_address(),
            'city': fake.city(),
            'country': 'Canada',
            'province': fake.state(),
            'postal': fake.postalcode()
        },
        'credit_card': {
            'name': 'Test Name',
            'number': '4242424242424242',
            'ccv': '123',
            'exp_year': '2027',
            'exp_month': '2',
        },
        'purchase_source_platform': 'psp_web'
    }

