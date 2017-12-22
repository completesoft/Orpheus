from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PlayerStatusSerializer
from .models import Player, Schedule, PlayerStatus, UpdateFile
from .serializers import ScheduleSerializer, UpdateFileSerializer
from .supp_func import is_auth_player



@api_view(['POST'])
def player_status(request, player_id):
    try:
        player = Player.objects.get(player_id=player_id)
    except Player.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if not is_auth_player(request, player_id):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer = PlayerStatusSerializer(player.status, data=request.data)
    if serializer.is_valid():
        serializer.save()
    if player.schedule and (player.status.status==1 or player.schedule.change_time.toordinal()>player.status.current_sch_time.toordinal()):
        print('SEND SCH')
        schedule = Schedule.objects.get(pk=player.schedule.id)
        sch_serial = ScheduleSerializer(schedule)
        cmd = {'cmd': 1}
        cmd.update({'Schedule': sch_serial.data})
        return Response(cmd, status=status.HTTP_200_OK)
    if player.update_granted:
        print('UP Granted')
        if player.send_updater:
            try:
                updater = UpdateFile.objects.filter(file_type='updater.py').latest()
            except UpdateFile.DoesNotExist as err:
                cmd = {'cmd': 0}
                print('EXception ', err)
                return Response(cmd, status=status.HTTP_200_OK)
            updater_ser = UpdateFileSerializer(updater, context={'request': request})
            cmd = {'cmd': 2}
            cmd.update({'Update': updater_ser.data})
            print('updater ', cmd)
            player.send_updater = False
            player.save(update_fields=['send_updater'])
            return Response(cmd, status=status.HTTP_200_OK)
        try:
            up_player = UpdateFile.objects.filter(file_type='api_player.py').latest()
        except UpdateFile.DoesNotExist as err:
            cmd = {'cmd': 0}
            return Response(cmd, status=status.HTTP_200_OK)
        if player.status.player_version < up_player.version and player.status.updater_present:
            up_player_ser = UpdateFileSerializer(up_player)
            cmd = {'cmd': 2}
            cmd.update({'Update': up_player_ser.data})
            print('Player ', cmd)
            return Response(cmd, status=status.HTTP_200_OK)
    cmd = {'cmd': 0}
    return Response(cmd, status=status.HTTP_400_BAD_REQUEST)





