import vlc
import time
import datetime

ALIVE_DELAY_SEC = 1
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 0

DEFAULT_URL = 'http://ic3.101.ru:8000/v3_1'

DEBUG_REKLAMA_1 = "19:23:00"
DEBUG_REKLAMA_2 = "20:27:30"


def send_alive():
    print("Send hive alive request")


i = vlc.Instance('--verbose={0} --network-caching={1}'.format(VERBOSE_LEVEL, NETWORK_CACHE_MS).split())
p = i.media_player_new()    # player for main stream
p.set_mrl(DEFAULT_URL)      # set main stream url

p_r = i.media_player_new()  # player for reklama


schedule = [{"desc": "r_1", "time": "19:22:00", "state": "ready", "url": 'http://hive.product.in.ua/music/reklama_1.mp3'},
            {"desc": "r_2", "time": "19:24:00", "state": "ready", "url": 'http://hive.product.in.ua/music/reklama_2.mp3'}]

p.play()    # start main stream

# debug_time = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(seconds=5), "%H:%M:%S")
# schedule[0]["time"] = debug_time

# DEBUG!!!
schedule[0]["time"] = DEBUG_REKLAMA_1
schedule[1]["time"] = DEBUG_REKLAMA_2

while True:

    print(schedule)
    current_time = datetime.datetime.strftime(datetime.datetime.now(), "%H:%M:%S")

    print(current_time)

    for task in schedule:
        # delta time = task time + 1 minute
        delta_time = datetime.datetime.strftime(datetime.datetime.strptime(task["time"], "%H:%M:%S") + datetime.timedelta(minutes=1), "%H:%M:%S")
        if task["time"] <= current_time <= delta_time:  # if time in interval then run task
            if task["state"] == "ready":
                print("start {}".format(task["desc"]))

                p_r.set_mrl(task["url"])    # set url for reklama

                for x in range(1, 5):
                    print("volume down")
                    p.audio_set_volume((10-x)*10)
                    time.sleep(1)

                p_r.play()  # start reklama
                time.sleep(1)
                print("reklama start!!!")

            if task["state"] == "ready" and p_r.is_playing():
                task["state"] = "playing"
                print("state play")

            if task["state"] == "playing" and not p_r.is_playing():
                    task["state"] = "old"
                    # p.play()
                    for x in range(5, 11):
                        print("volume up")
                        p.audio_set_volume(x * 10)
                        time.sleep(1)

    # is_playing = vlc.libvlc_media_player_is_playing(p)
    # print(is_playing)
    # if not is_playing:
    #     p.stop()
    #     print("restart")
    #     p.play()
    time.sleep(1)
    # # send_alive()

