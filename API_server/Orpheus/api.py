from rest_framework import generics, permissions
from .serializers import ScheduleSerializer
from .models import Schedule

class ScheduleDetail(generics.RetrieveAPIView):
    model = Schedule
    serializer_class = ScheduleSerializer
    lookup_url_kwarg = 'pk'
    queryset = Schedule.objects.all()


