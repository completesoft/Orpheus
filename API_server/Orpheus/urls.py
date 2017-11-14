from django.conf.urls import url, include

from .api import ScheduleDetail


app_name = 'Orpheus'


urlpatterns = [
    url(r'^(?P<pk>\d+)/$', ScheduleDetail.as_view(), name='schedule-detail'),
]
