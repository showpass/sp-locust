import time
from random import choice, random

from locust import task

import settings
from tasks.base import BaseUserTaskSet, BaseTaskSet
from tasks.generators import now_with_tz, user_based_basket


class UserViewTaskSet(BaseUserTaskSet):

    @task(1)
    def profile_tickets_task(self):
        self.get('/user/tickets/')
        return self.api_calls_tix()

    def api_calls_tix(self):
        resp = self.get(
            '/api/user/tickets/items/groups/?event__ends_on_gte=%s&is_redeemable=true&item_type=ticket&ordering=event__starts_on&page=1&page_size=10' % now_with_tz(),
            name='/api/user/tickets/item/groups/?QUERY')
        if resp.ok:
            groups = resp.json()['results']
            event_ids = set([x['event'] for x in groups])

            for event_id in event_ids:
                self.get('/api/public/events/%s/' % event_id, name='/api/public/events/[ID]/')

            return groups

        return None

    @task(1)
    def download_tix_task(self):
        groups = self.profile_tickets_task()
        try:
            group = choice(groups)
            self.get('/tickets/items/groups/%s/pdf/' % group['id'], name='/tickets/items/groups/[ID]/pdf/')
        except IndexError:
            self.buy_cart()
            self.download_tix_task()

    @task(1)
    def profile_products_task(self):
        self.get('/user/products/')
        return self.api_calls_products()

    def api_calls_products(self):
        resp = self.get('/api/user/tickets/items/groups/?is_redeemable=true&item_type=product&page=1&page_size=2',
                        name='/api/user/tickets/items/groups/?QUERY')
        if resp.ok:
            groups = resp.json()['results']
            product_ids = set([x['product'] for x in groups])

            for product_id in product_ids:
                self.get('/api/public/products/%s/' % product_id, name='/api/public/products/[ID]/')

            return groups

        return None

    @task(1)
    def download_product_task(self):
        groups = self.profile_products_task()
        try:
            group = choice(groups)
            self.get('/tickets/items/groups/%s/pdf/' % group['id'], name='/tickets/items/groups/[ID]/pdf/')
        except IndexError:
            pass

    @task(1)
    def profile_vouchers_task(self):
        self.get('/user/vouchers/')
        resp = self.get('/api/user/financials/discounts/?is_redeemable=true&page=1&page_size=10',
                        name='/api/user/financials/discounts/?QUERY')
        if resp.ok:
            groups = resp.json()['results']
            venue_ids = set([x['venue'] for x in groups])

            for venue_id in venue_ids:
                self.get('/api/public/venues/%s/' % venue_id, name='/api/public/venues/[ID]/')

            return groups

        return None

    @task(1)
    def profile_invoices_task(self):
        self.get('/user/invoices/')
        resp = self.get('/api/user/financials/invoices/?page=1', name='/api/user/financials/invoices/?QUERY')
        if resp.ok:
            invoices = resp.json()['results']
            return invoices

        return None

    @task(1)
    def download_invoice_task(self):
        invoices = self.profile_invoices_task()
        try:
            invoice = choice(invoices)
            self.get('/financials/invoices/%s/pdf/' % invoice['transaction_id'],
                     name='/financials/invoices/[ID]/pdf/')
        except IndexError:
            self.buy_cart()
            self.download_invoice_task()

    @task(1)
    def profile_profile_task(self):
        self.get('/user/profile/')

    @task(1)
    def profile_transfer_task(self):
        self.get('/user/transfer/')
        tix = self.api_calls_tix()
        products = self.api_calls_products()

    def on_start(self):
        self.set_crsf()
        new_user = self.create_user()
        self.set_crsf()
        self.login(new_user['email'], 'password')


class UserApiTaskSet(BaseUserTaskSet):

    @task(1)
    def add_tix_to_cart(self):
        self.add_tix()

    @task(1)
    def buy_tix(self):
        self.buy_cart()

    def on_start(self):
        self.set_crsf()
        new_user = self.create_user()
        self.set_crsf()
        self.get_public_events()
        self.login(new_user['email'], 'password')


class PublicViewTaskSet(BaseUserTaskSet):

    @task(1)
    def view_random_event(self):
        event_slug = choice(self._available_events['results'])['slug']
        self.get('/%s/' % event_slug, name='/[EVENT SLUG]/')

    @task(1)
    def view_random_venue(self):
        try:
            venue_slug = choice(self._available_venues)['slug']
            self.get('/o/%s/' % venue_slug, name='/o/[ORG SLUG]/')
        except IndexError:
            pass

    @task(1)
    def homepage(self):
        self.get('/')

    def on_start(self):
        self._available_events = self.get_public_events()
        self._available_venues = self.get_public_venues()


class PublicAPITaskSet(BaseTaskSet):
    @task(1)
    def events(self):
        self.get('/api/public/events/')

    @task(1)
    def venues(self):
        self.get('/api/public/venues/')

    @task(1)
    def products(self):
        self.get('/api/public/products/')

    @task(1)
    def widgets(self):
        self.get('/api/public/widgets/')

    @task(1)
    def survey_requirments(self):
        self.get('/api/public/surveys/requirements/')

    def geoip(self):
        self.get('/api/public/geoip/')


class TicketPurchaserTaskSet(BaseTaskSet):
    event_slug = settings.EVENT_SLUG
    ticket_type_id = settings.TEST_TICKET_TYPE
    email = settings.CUSTOMER_EMAIL
    password = settings.CUSTOMER_PASSWORD

    @task(1)
    def index_task(self):
        self.get('/')

    @task(1)
    def event_page_task(self):
        self.get('/%s/' % self.event_slug)

    @task(1)
    def event_api_task(self):
        self.get('/api/public/events/%s/' % self.event_slug)

    @task(3)
    def create_basket_task(self):
        self.post(
            '/api/user/tickets/baskets/',
            json=user_based_basket(tix_type=self.ticket_type_id, tix_quantity=2),
        )

    @task(1)
    def checkout_task(self):
        self.get('/checkout/')

    def on_start(self):
        self.set_crsf()
        self.login(self.email, self.password)
        self.set_crsf()


class FrontendViewerTaskSet(BaseTaskSet):
    email = settings.CUSTOMER_EMAIL
    password = settings.CUSTOMER_PASSWORD
    event_slugs = settings.EVENT_SLUGS

    @task(1)
    def index_task(self):
        self.get('/')

    @task(1)
    def event_page_task(self):
        self.get('/%s/' % random.choice(self.event_slugs))

    @task(1)
    def event_api_task(self):
        self.get('/api/public/events/%s/' % random.choice(self.event_slugs))

    @task(1)
    def login_task(self):
        self.login(self.email, self.password)
        self.set_crsf()

    def on_start(self):
        self.set_crsf()

EVENT_ID = settings.TEST_EVENT
TICKET_TYPE_ID = settings.TEST_TICKET_TYPE
TICKET_TYPE_ID_CHILD = settings.TICKET_TYPE_ID_CHILD

class PerformanceBasket(BaseTaskSet):
    # def on_start(self):
    #     self.event = self._events()['results'][0]

    def _events(self):
        resp = self.get(f'/api/public/events/?is_featured=true&page=1&page_size=12&id__in={EVENT_ID}')
        if resp.ok:
            return resp.json()
        else:
            return {}

    # @task(1)
    # def event_list(self):
    #     self.get('/api/public/events/?is_featured=true&page=1&page_size=12')

    @task(5)
    def add_to_basket_2(self):
        data = {
            'item_groups': [
                {
                    'item_type': 'ticket',
                    'quantity': 2,
                    'scan_codes': [],
                    'survey_responses': [],
                    'tt_seat_permissions': [],
                    'type': TICKET_TYPE_ID
                }
            ]
        }

        self.post('/api/user/tickets/baskets/', json=data)

    @task(5)
    def add_to_basket_1(self):
        data = {
            'item_groups': [
                {
                    'item_type': 'ticket',
                    'quantity': 1,
                    'scan_codes': [],
                    'survey_responses': [],
                    'tt_seat_permissions': [],
                    'type': TICKET_TYPE_ID
                }
            ]
        }

        self.post('/api/user/tickets/baskets/', json=data)

    @task(5)
    def add_to_basket_child(self):
        data = {
            'item_groups': [
                {
                    'item_type': 'ticket',
                    'quantity': 1,
                    'scan_codes': [],
                    'survey_responses': [],
                    'tt_seat_permissions': [],
                    'type': TICKET_TYPE_ID_CHILD
                }
            ]
        }

        self.post('/api/user/tickets/baskets/', json=data)

class FrontPage(BaseTaskSet):
    @task(1)
    def api_front_page(self):
        self.get('/api/public/events/?is_featured=true&page=1&page_size=12')


class AttractionUserTaskSet(BaseUserTaskSet):
    """
    Will run an attraction event load test for the given attraction event id in the settings.
    AttractionUserTaskSet will either purchase a timeslot for the attraction event,
    simply call the apis to view the events, or add some to cart and not checkout.

    The attraction event id provided must be set up so that all the events in the attraction config are recurring events
    with multiple timeslots within 24 hours of each-other.
    (So that they appear grouped in the calendar under a single day.)
    """
    event = settings.ATTRACTION_EVENT_ID

    def view_and_get_child_timeslot(self):
        resp = self.get(f'/api/public/events/{self.event}')
        attraction_config = resp.json()['attraction_event_config']
        venue_slug = resp.json()['venue']['slug']
        venue_id = resp.json()['venue']['id']
        event_ids = []
        for item in attraction_config:
            if item['type'] == 1:  # 1 means events.
                event_ids = item['ids']

        time.sleep(2)

        # Now we call normal calendar endpoint.
        events_string = ','.join([str(n) for n in event_ids])
        self.get(
            f'/api/public/venues/{venue_slug}/calendar/?venue__in={venue_id}&only_parents=true&event__in={events_string}')

        time.sleep(2)

        # Now we call for a random event in the calendar.
        random_event = choice(event_ids)
        day_event = self.get(f'/api/public/events/{random_event}/calendar')
        child_events = day_event.json()['child_events']

        if child_events:
            time.sleep(2)

            child_event = choice(child_events)
            child_slug = child_event['slug']
            resp = self.get(f'/api/public/events/{child_slug}/calendar')
            return resp.json()
        else:
            return day_event.json()

    @task(3)
    def view_event(self):
        """
        Task where a user goes and queries for the attraction event, opens the attraction calendar.
        Selects a day, then selects a timeslot. But does not do anything else.
        """
        self.view_and_get_child_timeslot()

    @task(2)
    def create_basket(self):
        """
        Task where a user goes and queries for the attraction event, opens the attraction calendar.
        Selects a day, then selects a timeslot. Then adds some tickets to their basket before promptly leaving the site.
        """
        child_data = self.view_and_get_child_timeslot()
        # Now that we have the child timeslot we will select a random ticket type and create a basket.
        time.sleep(2)

        tts = child_data['ticket_types']
        random_tt = choice(tts)

        self.post(
            '/api/user/tickets/baskets/',
            json=user_based_basket(tix_type=random_tt['id'], tix_quantity=2),
        )

    @task(1)
    def purchase_event(self):
        child_data = self.view_and_get_child_timeslot()
        # Now that we have the child timeslot we will select a random ticket type and create a basket.
        time.sleep(2)

        tts = child_data['ticket_types']
        random_tt = choice(tts)

        basket_data = self.post(
            '/api/user/tickets/baskets/',
            json=user_based_basket(tix_type=random_tt['id'], tix_quantity=2),
        )

        time.sleep(2)

        # Now purchase the tickets.
        self._basket_data = basket_data.json()
        self.buy_cart()

    def on_start(self):
        self.set_crsf()
        new_user = self.create_user()
        self.set_crsf()
        self.login(new_user['user']['email'], 'password')


class SingleEventLoadTest(BaseUserTaskSet):
    """
    Will run a load test for a single GA event. Good way to test high concurrency purchase of the same ticket types.
    """
    event = settings.SINGLE_TEST_EVENT

    def view_event_and_get_tt(self):
        resp = self.get(f'/api/public/events/{self.event}')

        time.sleep(2)

        event = resp.json()

        # Now we call for a random event in the calendar.
        random_tt = choice(event['ticket_types'])
        return random_tt

    @task(1)
    def view_event(self):
        """
        Task where a user goes and queries for the attraction event, opens the attraction calendar.
        Selects a day, then selects a timeslot. But does not do anything else.
        """
        self.view_event_and_get_tt()

    @task(1)
    def create_basket(self):
        """
        Task where a user goes and queries for the attraction event, opens the attraction calendar.
        Selects a day, then selects a timeslot. Then adds some tickets to their basket before promptly leaving the site.
        """
        tt = self.view_event_and_get_tt()
        # Now that we have the child timeslot we will select a random ticket type and create a basket.
        time.sleep(2)

        self.post(
            '/api/user/tickets/baskets/',
            json=user_based_basket(tix_type=tt['id'], tix_quantity=2),
        )

    @task(1)
    def purchase_event(self):
        tt = self.view_event_and_get_tt()
        time.sleep(2)

        basket_data = self.post(
            '/api/user/tickets/baskets/',
            json=user_based_basket(tix_type=tt['id'], tix_quantity=2),
        )
        time.sleep(2)
        # Now purchase the tickets.
        self._basket_data = basket_data.json()
        self.buy_cart()

    def on_start(self):
        self.set_crsf()
        new_user = self.create_user()
        self.set_crsf()
        self.login(new_user['user']['email'], 'password')