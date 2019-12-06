from locust import task

from base import BaseTaskSet, BaseVenueUserTaskSet

user_emails = []


class VenueUser(BaseVenueUserTaskSet):

    def on_start(self):
        global user_emails
        self.set_crsf()
        new_user = self.create_user()
        self.set_crsf()
        self.login(new_user['email'], 'password')
        self.venue = self.get_or_create_venue()
        user_emails.append(new_user['email'])


class DashboardViewTaskSet(VenueUser):

    def landing(self):
        self.get('/dashboard/landing/')


class VenueStatsAPITaskSet(VenueUser):

    def stats_reservations_booked(self):
        self.get('/api/venue/%s/reservations/booked/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/reservations/booked/')

    def analytics_daily_stats(self):
        self.get('/api/venue/%s/analytics/daily-stats/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/analytics/daily-stats/')

    def analytics_daily_stats_customers(self):
        self.get('/api/venue/%s/analytics/daily-stats/customers/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/analytics/daily-stats/customers/')

    def analytics_daily_stats_employees(self):
        self.get('/api/venue/%s/analytics/daily-stats/employees/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/analytics/daily-stats/employees/')


class VenueAPIEventsTaskSet(VenueUser):

    def venue_events(self):
        self.get('/api/venue/%s/events/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/events/')

    def event_access(self):
        self.get('/api/venue/%s/event-accesses/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/event-accesses/')


class VenueAPIOthersTaskSet(VenueUser):

    def user_venue_employments(self):
        self.get('/api/user/venues/employments/')

    def user_venue_employments_roles(self):
        self.get('/api/user/venues/employments/roles/')


class VenueFinancialAPITaskSet(VenueUser):

    def financial_invoices(self):
        self.get('/api/venue/%s/financials/invoices/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/financials/invoices/')

    def financial_discounts(self):
        self.get('/api/venue/%s/financials/discounts/' % self.venue['id'],
                 name='/api/venue/[VENUE ID]/financials/discounts/')


class EventAdministrationTaskSet(VenueUser):

    @task(5)
    def create_event_task(self):
        """
        /api/venue/events/
        """
        self.create_event()

    @task(1)
    def edit_event_task(self):
        """
        This will just change the ticket inventory
        """
        self.edit_event()


class VenueAdministrationTaskSet(VenueUser):

    @task(1)
    def change_venue_task(self):
        self.change_to_random_venue()

    def on_start(self):
        super(VenueAdministrationTaskSet, self).on_start()
        for x in range(1, 4):
            self.create_venue()


class StatisticsTaskSet(BaseTaskSet):
    pass


class BoxOfficeTaskSet(BaseTaskSet):

    def sell_tix_task(self):
        pass

    def sell_product_task(self):
        pass
