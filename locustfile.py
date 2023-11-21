from locust import HttpUser, between

import settings
from tasks.front import PerformanceBasket, FrontPage, AttractionUserTaskSet, SingleEventLoadTest

if settings.PERF_ENABLED:
    """
    Deprecated
    """
    class PerformanceUser(HttpUser):
        tasks = {PerformanceBasket: 1}
        wait_time = between(5, 10)


if settings.FRONT_PAGE_ENABLED:
    """
    Deprecated
    """
    class FrontPageUser(HttpUser):
        tasks = {FrontPage: 1}
        wait_time = between(5, 10)

if settings.ATTRACTION_EVENT_TEST_ENABLED:
    """
    If true we will run an attraction event load test for the given attraction event id in the settings.
    This test will spawn an AttractionEventUser which will either purchase a timeslot for the attraction event, 
    simply call the apis to view the events, or add some to cart and not checkout.
    
    The attraction event id provided must be set up so that all the events in the attraction config are recurring events
    with multiple timeslots within 24 hours of each-other. 
    (So that they appear grouped in the calendar under a single day.)
    """
    class AttractionEventUser(HttpUser):
        wait_time = between(5, 10)
        tasks = {AttractionUserTaskSet: 1}

if settings.SINGLE_EVENT_LOAD_TEST_ENABLED:
    """
    If true we will run a single normal event GA load test. Includes viewing/basket-creation/purchasing.
    """

    class AttractionEventUser(HttpUser):
        wait_time = between(5, 10)
        tasks = {SingleEventLoadTest: 1}
