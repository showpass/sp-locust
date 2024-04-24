# Settings file for the locustfile.py

# Deprecated constants
PERF_ENABLED = False
FRONT_PAGE_ENABLED = False
TEST_EVENT = 212
TEST_TICKET_TYPE = 738  #4483
TICKET_TYPE_ID_CHILD = 738 #739
CUSTOMER_EMAIL = 'dev@showpass.com'
CUSTOMER_PASSWORD = 'password'
EVENT_SLUGS = ['event-a', 'event-b', 'event-c']
EVENT_SLUG = 'event-slug-a'

# Non-deprecated constants.
REQUEST_OPTS = dict(
    verify=False,  # Ignore SSL errors (helps for testing on live server)
)


# Settings for enabling attraction event load test.
ATTRACTION_EVENT_TEST_ENABLED = False
ATTRACTION_EVENT_ID = 62559

# Settings for enabling single GA event load test.
SINGLE_EVENT_LOAD_TEST_ENABLED = False
SINGLE_TEST_EVENT = 82676

# Settings for enabling single GA Location event load test.
SINGLE_EVENT_GA_LOCATION_LOAD_TEST_ENABLED = True
LOCATION_TEST_EVENT = 82668
LOCATION_TEST_PERMISSION = 5715

# Settings for enabling single GA Location event load test.
SINGLE_MEMBERSHIP_GA_LOCATION_LOAD_TEST_ENABLED = True
LOCATION_TEST_MEMBERSHIP = 10739
LOCATION_MEMBERSHIP_BENEFIT = 5012
MEMBERSHIP_LOCATION_TEST_PERMISSION = 5717
