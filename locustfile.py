from locust import HttpUser

import settings
from tasks.front import PerformanceBasket, FrontPage

if settings.PERF_ENABLED:
    class PerformanceUser(HttpUser):
        task_set = PerformanceBasket
        min_wait = 500
        max_wait = 1000


if settings.FRONT_PAGE_ENABLED:
    class FrontPageUser(HttpUser):
        task_set = FrontPage
        min_wait = 500
        max_wait = 1000
