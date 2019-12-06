from locust import HttpLocust

import settings
from tasks.front import PerformanceBasket, FrontPage

if settings.PERF_ENABLED:
    class PerformanceUser(HttpLocust):
        task_set = PerformanceBasket
        min_wait = 500
        max_wait = 1000


if settings.FRONT_PAGE_ENABLED:
    class FrontPageUser(HttpLocust):
        task_set = FrontPage
        min_wait = 500
        max_wait = 1000