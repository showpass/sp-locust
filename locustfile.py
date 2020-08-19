from locust import HttpUser, between

import settings
from tasks.front import PerformanceBasket, FrontPage

if settings.PERF_ENABLED:
    class PerformanceUser(HttpUser):
        tasks = {PerformanceBasket: 1}
        wait_time = between(5, 10)


if settings.FRONT_PAGE_ENABLED:
    class FrontPageUser(HttpUser):
        tasks = {FrontPage: 1}
        wait_time = between(5, 10)
