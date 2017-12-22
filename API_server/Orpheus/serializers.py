from rest_framework import serializers
from .models import Schedule, Silent, Inserts, MainStream, PlayerStatus, Player, UpdateFile


class MainStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainStream
        fields = ('url', 'volume', 'description')


class InsertsSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format='%H:%M:%S')

    class Meta:
        model = Inserts
        fields = ('description', 'url', 'time', 'volume')


class SilentSerializer(serializers.ModelSerializer):
    time_start = serializers.TimeField(format='%H:%M:%S')
    time_end = serializers.TimeField(format='%H:%M:%S')

    class Meta:
        model = Silent
        fields = ('description', 'time_start', 'time_end')


class ScheduleSerializer(serializers.ModelSerializer):
    change_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    main_stream = MainStreamSerializer(read_only=True)
    inserts = InsertsSerializer(many=True, read_only=True)
    silent = SilentSerializer(many=True, read_only=True)


    class Meta:
        model = Schedule
        fields = ('title', 'change_time', 'main_stream', 'inserts', 'silent')


class PlayerStatusSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(read_only=True)
    timestamp = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    current_sch_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False, default=None)

    class Meta:
        model = PlayerStatus
        fields = ('player', 'status', 'timestamp', 'current_sch_time', 'player_version', 'updater_present')


class UpdateFileSerializer(serializers.ModelSerializer):


    class Meta:
        model = UpdateFile
        fields = ('file_type', 'url')
