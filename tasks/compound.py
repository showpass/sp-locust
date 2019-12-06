from front import UserViewTaskSet, UserApiTaskSet, PublicViewTaskSet, PublicAPITaskSet
from tasks.dashboard import EventAdministrationTaskSet, VenueAdministrationTaskSet
from base import BaseVenueUserTaskSet, BaseUserTaskSet


class UserTaskSet(UserViewTaskSet, UserApiTaskSet):
    pass


class PublicTaskSet(PublicViewTaskSet, PublicAPITaskSet):
    pass


class VenueEventAdminTaskSet(EventAdministrationTaskSet, VenueAdministrationTaskSet):
    pass
