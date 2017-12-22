from django.conf import settings
import hashlib


def is_auth_player(request, player_id):
    compare = hashlib.md5()
    compare.update((getattr(settings, 'SECRET')).encode())
    compare.update((player_id).encode())
    return request.POST['sig'] == compare.hexdigest()
