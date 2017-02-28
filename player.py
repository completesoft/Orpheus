import vlc
import time

ALIVE_DELAY_SEC = 60
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 0

DEFAULT_URL = 'http://ic3.101.ru:8000/v3_1'


def send_alive():
    print("Send hive alive")


i = vlc.Instance('--verbose={0} --network-caching={1}'.format(VERBOSE_LEVEL, NETWORK_CACHE_MS).split())
p = i.media_player_new()
p.set_mrl(DEFAULT_URL)

while True:
    is_playing = vlc.libvlc_media_player_is_playing(p)
    print(is_playing)
    if not is_playing:
        p.stop()
        print("restart")
        p.play()
    time.sleep(ALIVE_DELAY_SEC)
    send_alive()






    # for x in range(1,6):
    #     time.sleep(1)
    #     print(x)
    #
    # p.stop()
    # p.set_mrl('http://ic4.101.ru:8000/p193366')
    # p.play()
    # pass
