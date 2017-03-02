import vlc
import datetime
import time
import requests
import copy


ALIVE_DELAY_SEC = 1
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 0
DEBUG = True
TIME_FORMAT = "%H:%M:%S"
URL = "http://hive.product.in.ua:8885/api"
# URL = "http://localhost:8885/api"

# Quantity of loops main "While"-cycle
PERIOD_UPDATE = 10


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


def fade_out(player):
    for x in range(1, 6):
        print("volume down")
        player.audio_set_volume((10 - x) * 10)
        time.sleep(1)


def fade_in(player):
    for x in range(6, 11):
        print("volume up")
        player.audio_set_volume(x * 10)
        time.sleep(1)


# Receive schedule at the beginning
schedule = req_schedule()
inserts_array = copy.deepcopy(schedule["inserts"])

i = vlc.Instance('--verbose={0} --network-caching={1}'.format(VERBOSE_LEVEL, NETWORK_CACHE_MS).split())

# player for main stream
p_main = i.media_player_new()

# player for advertising
p_r = i.media_player_new()

# set main stream url
p_main.set_mrl(schedule["main_stream"]["url"])
p_main.audio_set_volume(schedule["main_stream"]["volume"])

p_main.play()

# Counter for update method
counter_update = 0
sleep_flag = False

while True:
    # for something
    time.sleep(1)

    counter_update += 1
    if DEBUG:
        print("COUNTER: "+str(counter_update))

    # Update schedule
    if counter_update > PERIOD_UPDATE:
        main_stream_old = schedule["main_stream"]["url"]
        try:
            new_schedule = req_schedule()
        except:
            print("API timeout")
        else:
            if new_schedule != schedule:
                if DEBUG:
                    print("New schedule arrived")
                    print("--------------------")
                    print(schedule)
                    print(new_schedule)
                    print("--------------------")

                schedule = new_schedule
                inserts_array = copy.deepcopy(schedule["inserts"])

            if DEBUG:
                print(schedule)
            if main_stream_old != schedule["main_stream"]["url"]:
                p_main.stop()
                p_main.set_mrl(schedule["main_stream"]["url"])
                p_main.audio_set_volume(schedule["main_stream"]["volume"])
            if not sleep_flag and not p_main.is_playing():
                if DEBUG:
                    print("restart stream")
                p_main.stop()
                p_main.play()

        counter_update = 0

    # ####Check in "Silent"-zone
    for silent in schedule["silent"]:
        if silent["time_start"] <= current_time() <= silent["time_end"]:
            if not sleep_flag:
                fade_out(p_main)
                p_main.stop()
                sleep_flag = True
            break
        else:
            if sleep_flag:
                p_main.play()
                fade_in(p_main)
                sleep_flag = False

    if sleep_flag:
        continue
    #####

    # Check: are we in INSERTS

    for insert in inserts_array:
        cur_time = current_time()
        delta_t = delta_time(insert["time"])
        if DEBUG:
            print(insert)
        # if time in interval then run task
        if insert["time"] <= cur_time <= delta_t and "played" not in insert:
            # set url for reklama
            p_r.set_mrl(insert["url"])

            fade_out(p_main)

            # start reklama
            p_r.audio_set_volume(insert["volume"])
            p_r.play()
            time.sleep(1)

            while p_r.is_playing():
                time.sleep(1)

            # Flag: the insert's played
            insert["played"] = True

            fade_in(p_main)

    if not p_main.is_playing():
        p_main.stop()
        p_main.play()