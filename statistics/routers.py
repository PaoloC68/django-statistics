from django.conf import settings


STATISTICS_DB = getattr(settings, 'STATISTICS_DB', 'stats')
STATISTICS_APP_NAMES = ['statistics',]
class BaseRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label in STATISTICS_APP_NAMES:
            return STATISTICS_DB
        else:
            return None

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        if   obj1._meta.app_label in STATISTICS_APP_NAMES or\
             obj2._meta.app_label in STATISTICS_APP_NAMES:
            return True
        return None

    def allow_syncdb(self, db, model):
        "Make sure the myapp app only appears on the 'other' db"
        if db == STATISTICS_DB:
            return model._meta.app_label in STATISTICS_APP_NAMES
        elif model._meta.app_label in STATISTICS_APP_NAMES:
            return False
        return None    