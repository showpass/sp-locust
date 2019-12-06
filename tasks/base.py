from locust import TaskSet

import settings
from tasks.generators import user_based_venue, user_based_basket, user_based_cc_basket_purchase, cc_data, auth_user, \
    venue_based_event
from random import choice


class BaseTaskSet(TaskSet):
    jwt_token = None

    def __init__(self, *args, **kwargs):
        self.csrf_token = None
        super(BaseTaskSet, self).__init__(*args, **kwargs)

    def _set_kwargs(self, kwargs):
        headers = kwargs.pop('headers', {})

        if self.jwt_token:
            headers['Authorization'] = 'JWT %s' % self.jwt_token

        if self.csrf_token is not None:
            headers['X-CSRFToken'] = self.csrf_token
            headers['Referer'] = self.client.base_url

        new_kwargs = dict(kwargs, headers=headers, **settings.REQUEST_OPTS)
        new_kwargs['verify'] = True
        return new_kwargs

    def get(self, *args, **kwargs):
        kwargs = self._set_kwargs(kwargs)
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs = self._set_kwargs(kwargs)
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs = self._set_kwargs(kwargs)
        return self.client.put(*args, **kwargs)

    def set_crsf(self):
        r = self.get('')
        try:
            self.csrf_token = r.cookies['csrftoken']
        except KeyError:
            pass

    def login(self, email, password):
        self.client.headers['Referer'] = self.client.base_url

        response = self.post(
            '/api/auth/jwt/',
            json={
                'email': email, 'password': password,
            }
        )
        response.raise_for_status()

    def get_public_events(self):
        self._public_events = self.get('/api/public/events/?page_size=100').json()
        return self._public_events

    def get_public_venues(self):
        self._public_venues = self.get('/api/public/venues/').json()
        return self._public_venues


class BaseUserTaskSet(BaseTaskSet):
    def __init__(self, *args, **kwargs):
        self._basket_data = None
        self._has_tix = False
        self._current_venue = None
        self._user = None
        super(BaseUserTaskSet, self).__init__(*args, **kwargs)

    def create_user(self):
        """
        /api/auth/registration/
        """
        new_user_resp = self.post('/api/auth/registration/', json=auth_user())
        if new_user_resp.ok:

            self._user = new_user_resp.json()
            return self._user

        return None

    def make_cart(self):
        """
        /api/user/tickets/baskets/
        """
        return self.post('/api/user/tickets/baskets/', json=user_based_basket()).json()

    def add_tix(self):
        """
        /api/user/tickets/baskets/[ID]/
        """
        pub_evs = self.get_public_events()
        evs_rand = choice(pub_evs['results'])
        tix_random = choice(evs_rand['ticket_types'])
        if self._basket_data is None:
            self._basket_data = self.make_cart()

        resp = self.put('/api/user/tickets/baskets/%s/' % self._basket_data['id'],
                        json=user_based_basket(tix_random['id'],
                                               choice([1, 2, 3, 4, 5])),
                        name='/api/user/tickets/baskets/[BASKET ID]/')
        if resp.ok:
            self._basket_data = resp.json()
            self._has_tix = True
        return resp

    def buy_cart(self):
        if not self._has_tix:
            self.add_tix()

        if self._basket_data['total_price'] == '0.00':
            basket_json_data = {
                'basket': self._basket_data['id'],
                'id': self._basket_data['id'],
                'payment_type': 5
            }
        else:
            strip_resp = self.pay_stripe().json()
            basket_json_data = user_based_cc_basket_purchase(self._basket_data['id'], strip_resp['id'])

        resp = self.post('/api/user/tickets/baskets/%s/purchase/' % self._basket_data['id'],
                         json=basket_json_data, name='/api/user/tickets/baskets/[BASKET ID]/purchase/')

        if resp.ok:
            self._has_tix = False
            self._basket_data = None

        return resp.json()

    def get_or_create_venue(self, create=False):
        assert self.csrf_token is not None

        resp = self.get('/api/user/venues/session/get/')
        if resp.ok and not create:
            self._current_venue = resp.json()
        if self._current_venue is None or create:
            return self.create_venue()

        return self._current_venue

    def create_venue(self):
        """
        /api/user/venues/
        """
        assert self.csrf_token is not None
        email = None if self._user is None else self._user['email']
        resp = self.post('/api/user/venues/', json=user_based_venue(email=email))
        if resp.ok:
            self._current_venue = resp.json()
            return self._current_venue
        return None

    def pay_stripe(self):
        return self.post('https://api.stripe.com/v1/tokens', data=cc_data(), name='STRIPE')


class BaseVenueUserTaskSet(BaseUserTaskSet):

    def __init__(self, *args, **kwargs):
        self._venue_event_data = {}
        self._locations = None
        super(BaseVenueUserTaskSet, self).__init__(*args, **kwargs)

    def create_venue(self):
        venue = super(BaseVenueUserTaskSet, self).create_venue()
        if venue is not None:
            self._venue_event_data[venue['id']] = []
        return venue

    def change_venue(self, id):
        resp = self.put('/api/user/venues/session/%s/' % id, name='/api/user/venues/session/[VENUE ID]/')

        if resp.ok:
            self._current_venue = resp.json()
            return self._current_venue
        return None

    def change_to_random_venue(self):
        if len(self._venue_event_data.keys()) < 2:
            self.create_venue()
            return self.change_to_random_venue()
        else:
            return self.change_venue(choice(self._venue_event_data.keys()))

    def create_event(self):
        """
        /api/venue/events/
        """
        if self._current_venue is None:
            self.create_venue()
        if self._locations is None:
            resp = self.get('/api/venue/%s/events/locations/' % self._current_venue['id'],
                            name='/api/venue/[VENUE ID]/events/locations/')
            if resp.ok:
                self._locations = resp.json()

        event_data_raw = venue_based_event(self._locations[0]['id'])
        event_resp = self.post('/api/venue/events/', json=event_data_raw)

        if event_resp.ok:
            event = event_resp.json()
            self._venue_event_data[self._current_venue['id']].append(event)

            return event

        return None

    def edit_event(self):
        """
        This will just change the ticket inventory
        """
        if self._current_venue is None:
            self.create_venue()
        if len(self._venue_event_data[self._current_venue['id']]) == 0:
            event = self.create_event()
        else:
            event = choice(self._venue_event_data[self._current_venue['id']])

        event['tickettype_set'][0]['inventory'] += 1

        resp = self.put(
            '/api/venue/%s/events/%s/?id=%s' % (
                self._current_venue['id'],
                event['slug'],
                event['id']),
            json=event,
            name='/api/venue/[VENUE ID]/events/[EVENT ID]/?id=[EVENT ID]'
        )

        if resp.ok:
            return resp.json()

        return None

    def generate_basic(self, events=5, venues=1):
        for venue in range(0,venues):
            venue = self.create_venue()
            self.change_venue(venue['id'])
            for event in range(0, events):
                self.create_event()