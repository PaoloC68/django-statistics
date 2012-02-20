The official repository for ``django-statistics`` is at https://github.com/denz/django-statistics.

This is an attempt to improve the application


Configuration:

in settings.py for untrack some urls:
STATISTICS_UNTRACK_URLS = ["/favicon","/dajax","/jsi18n" ..... ]

INSTALLED_APP += (
	...
	'tracking',
	'visitor',
	'statistics',

)

MIDDLEWARE_CLASSES += (
	'tracking.middleware.VisitorTrackingMiddleware',
	'tracking.middleware.VisitorCleanUpMiddleware',
        'tracking.middleware.BannedIPMiddleware',

        'visitor.middleware.VisitorMiddleware',
)

SESSION_COOKIE_AGE = 3600
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

TRACKING_TIMEOUT = 1


