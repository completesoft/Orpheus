from django.conf.urls import url, include
from .api import ScheduleDetail
from .views import player_status

app_name = 'Orpheus'


urlpatterns = [
    # url(r'^(?P<pk>\d+)/$', ScheduleDetail.as_view(), name='schedule-detail'),
    url(r'^(?P<player_id>\w+)/$', player_status, name='status'),
]
