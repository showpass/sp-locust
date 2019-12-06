from locust.exception import StopLocust
from locust import task

from base import BaseVenueUserTaskSet


class SetupVenueUserTask(BaseVenueUserTaskSet):
    def on_start(self):
        self.set_crsf()
        new_user = self.create_user()
        self.set_crsf()
        self.login(new_user['email'], 'password')
        self.generate_basic()

    @task(1)
    def stop(self):
        raise StopLocust
