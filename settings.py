# Settings file for the locustfile.py

PERF_ENABLED = True
FRONT_PAGE_ENABLED = False
TEST_EVENT = 2146
TEST_TICKET_TYPE = 7
CUSTOMER_EMAIL = 'dev@showpass.com'
CUSTOMER_PASSWORD = 'password'
EVENT_SLUGS = ['event-a', 'event-b', 'event-c']
EVENT_SLUG = 'event-slug-a'

REQUEST_OPTS = dict(
    verify=False,  # Ignore SSL errors (helps for testing on live server)
)