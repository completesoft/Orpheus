import vlc
import datetime
import time
import requests


ALIVE_DELAY_SEC = 1
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 0
TIME_FORMAT = "%H:%M:%S"
# URL = "http://hive.product.in.ua:8885/api"
URL = "http://localhost:8885/api"

# Quantity of loops main "While"-cycle
PERIOD_UPDATE = 30


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

# Receive schedule at the beginning
schedule = req_schedule()

i = vlc.Instance('--verbose={0} --network-caching={1}'.format(VERBOSE_LEVEL, NETWORK_CACHE_MS).split())

# player for main stream
p_main = i.media_player_new()

# set main stream url
p_main.set_mrl(schedule["main_stream"]["url"])
p_main.audio_set_volume(schedule["main_stream"]["volume"])

# player for advertising
p_r = i.media_player_new()

p_main.play()

# Counter for update method
counter_update = 0

sleep_flag = False

while True:
    # for something
    time.sleep(1)

    counter_update += 1

    # Update schedule
    if counter_update > PERIOD_UPDATE:
        main_stream_old = schedule["main_stream"]["url"]
        schedule = req_schedule()
        if main_stream_old != schedule["main_stream"]["url"]:
            p_main.stop()
            p_main.set_mrl(schedule["main_stream"]["url"])
            p_main.audio_set_volume(schedule["main_stream"]["volume"])
        if not sleep_flag and not p_main.is_playing():
            p_main.play()
        counter_update = 0

    ##### Check in "Silent"-zone
    for silent in schedule["silent"]:
        if silent["time_start"] <= current_time() <= silent["time_end"]:
            p_main.stop()
            p_r.stop()
            sleep_flag = True
            break
        else:
            sleep_flag = False


    if sleep_flag:
        continue
    #####

    # Check: are we in INSERTS
    for inserts in schedule["inserts"]:
        cur_time = current_time()
        delta_t = delta_time(inserts["time"])

        # if time in interval then run task
        if inserts["time"] <= cur_time <= delta_t and "state" not in inserts.keys():

            # set url for reklama
            p_r.set_mrl(inserts["url"])

            for x in range(1, 6):
                print("volume down")
                p_main.audio_set_volume((10 - x) * 10)
                time.sleep(1)

            # start reklama
            p_r.play()
            time.sleep(1)

            while p_r.is_playing():
                time.sleep(1)

            # Flag: the insert's played
            inserts["state"] = False

            for x in range(5, 10):
                print("volume up")
                p_main.audio_set_volume(x * 10)
                time.sleep(1)

    if not p_main.is_playing():
        p_main.stop()
        p_main.play()