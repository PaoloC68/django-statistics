from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('statistics.views',
    	url(r'^recent_graph/$', 'recent_graph',  name='recent_graph'),
)
