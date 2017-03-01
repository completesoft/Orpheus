import vlc
import time
import datetime
import time
import requests
import json


ALIVE_DELAY_SEC = 1
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 0
TIME_FORMAT = "%H:%M:%S"
URL = "http://hive.product.in.ua:8885/api"
PERIOD_UPDATE = 60


def req_schedule():
    headers = {"content-type": "application/json"}
    data = {"action": "get_schedule", "id": 1}
    p = requests.post(URL, headers=headers, json=data)
    return p.json()


def current_time():
    return datetime.datetime.strftime(datetime.datetime.now(), TIME_FORMAT)


def delta_time(time_insert, minutes=1):
    p = datetime.datetime.strftime(datetime.datetime.strptime(time_insert, TIME_FORMAT) + datetime.timedelta(minutes=minutes), TIME_FORMAT)
    return p


schedule = req_schedule()

# DEBUG
# json.dump(schedule, open("schedule.json", "w"), indent=4, sort_keys=True)

i = vlc.Instance('--verbose={0} --network-caching={1}'.format(VERBOSE_LEVEL, NETWORK_CACHE_MS).split())

# player for main stream
p_main = i.media_player_new()

# set main stream url
p_main.set_mrl(schedule["main_stream"]["url"])
p_main.audio_set_volume(schedule["main_stream"]["volume"])

# player for advertising
p_r = i.media_player_new()

p_main.play()

count_start = current_time()

while True:

    # if datetime.datetime.strptime(schedule["silent"], TIME_FORMAT)
    count_end = current_time()
    if datetime.timedelta(minutes = count_end-count_start) > PERIOD_UPDATE:
        p_main.stop()
        schedule = req_schedule()
        p_main.audio_set_volume(schedule["main_stream"]["volume"])
        p_main.play()

    for adv_sing in schedule["inserts"]:
        # delta time = task time + 1 minute
        cur_time = current_time()
        delta_t = delta_time(adv_sing["time"])

        # if time in interval then run task
        if adv_sing["time"] <= cur_time <= delta_t and "state" not in adv_sing.keys():

            # set url for reklama
            p_r.set_mrl(adv_sing["url"])

            for x in range(1, 6):
                print("volume down")
                p_main.audio_set_volume((10-x)*10)
                time.sleep(1)

            # start reklama
            p_r.play()
            time.sleep(1)

            while p_r.is_playing():
                time.sleep(1)

            adv_sing["state"]= False

            for x in range(5, 11):
                print("volume up")
                p_main.audio_set_volume(x*10)
                time.sleep(1)

