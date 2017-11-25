import vlc
import datetime
import time
import requests
import copy
import json

# In URL - "localhost:8000" change to your DEPLOY server URL
########
URL = "http://localhost:8000/api/1/"
########


### ADV_DELAY Must be grater when CYCLE_DELAY_SEC
ADV_DELAY = datetime.timedelta(seconds=10)
#
CYCLE_DELAY_SEC = 5
###
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 2
DEBUG = True
FILE_LAST_SCHEDULE = 'last_schedule.json'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'
MAIN_PLAYER_MIN_VOLUME = 10


class Player(object):

    def __init__(self):
        self.vlc_instance = vlc.Instance('--verbose={0} --network-caching={1}'.format(VERBOSE_LEVEL, NETWORK_CACHE_MS).split())
        self.current_schedule = None
        self.raw_schedule = None
        self.main_player = self.vlc_instance.media_player_new()
        self.adv_player = self.vlc_instance.media_player_new()
        self.main_player_change = True
        self.sleep_flag = False
        self.sleep_time = None

    def is_change_sch(self):
        if self.current_schedule is None:
            sch = self.get_local_schedule()
            if sch is not None:
                self.raw_schedule = sch
                self.format_raw_schedule()
                self.set_schedule()
            self.request_schedule()
            return self.compare()
        else:
            self.request_schedule()
            return self.compare()

    def compare(self):
        if self.current_schedule is None and self.raw_schedule is not None:
            return True
        if self.current_schedule is not None and self.raw_schedule is None:
            return False
        if self.current_schedule is not None and self.raw_schedule is not None:
            return self.is_new_schedule()
        return False

    def get_local_schedule(self):
        print('GET local')
        try:
            with open(FILE_LAST_SCHEDULE) as file:
                schedule = json.load(file)
        except (FileExistsError, FileNotFoundError) as error:
            print(error)
            return None
        return schedule

    def save_schedule(self):
        with open(FILE_LAST_SCHEDULE, "w") as file:
            json.dump(self.raw_schedule, file, indent=4)

    def set_schedule(self):
        self.main_player_change = True
        self.sleep_flag = False
        self.sleep_time = None
        self.current_schedule = copy.deepcopy(self.raw_schedule)
        self.raw_schedule = None

    def request_schedule(self):
        try:
            raw_schedule = requests.get(URL)
        except requests.exceptions.ConnectionError as error:
            print(error)
            return None
        self.raw_schedule = raw_schedule.json()

    def is_new_schedule(self):
        new = datetime.datetime.strptime(self.raw_schedule['change_time'], DATETIME_FORMAT)
        old = self.current_schedule['change_time']
        return not new == old

    def format_raw_schedule(self):
        if self.raw_schedule:
            self.raw_schedule['change_time'] = datetime.datetime.strptime(self.raw_schedule['change_time'], DATETIME_FORMAT)
            for silent in self.raw_schedule['silent']:
                silent['time_start'] = datetime.datetime.strptime(silent['time_start'], TIME_FORMAT).time()
                silent['time_end'] = datetime.datetime.strptime(silent['time_end'], TIME_FORMAT).time()
            for insert in self.raw_schedule['inserts']:
                insert['time'] = datetime.datetime.strptime(insert['time'], TIME_FORMAT).time()

#ade_out vol to MAIN_PLAYER_MIN_VOLUME
    def fade_out_main_player(self):
        if self.main_player.is_playing():
            curr_volume = self.main_player.audio_get_volume()
            if curr_volume>MAIN_PLAYER_MIN_VOLUME:
                curr_volume = curr_volume - curr_volume%10
                self.main_player.audio_set_volume(curr_volume)
                for i in range(1, (curr_volume-10)//10):
                    self.main_player.audio_set_volume(curr_volume- i * 10)
                    time.sleep(2)

#current volume = MAIN_PLAYER_MIN_VOLUME
    def fade_in_main_player(self):
        required_volume = self.current_schedule['main_stream']['volume']
        if required_volume > MAIN_PLAYER_MIN_VOLUME:
            curr_volume = MAIN_PLAYER_MIN_VOLUME + required_volume % 10
            self.main_player.audio_set_volume(curr_volume)
            for i in range(1, (required_volume-curr_volume+10)//10):
                self.main_player.audio_set_volume(curr_volume+i*10)
                time.sleep(2)

    def get_adv_player(self):
        for insert in self.current_schedule['inserts']:
            campare_time = datetime.datetime.combine(datetime.date.today(), insert['time'])
            if campare_time<=datetime.datetime.now()<=campare_time+ADV_DELAY:
                self.adv_player.set_mrl(insert['url'])
                self.adv_player.audio_set_volume(insert['volume'])
                return True
        return False

    def run_adv_player(self):
        self.adv_player.play()
        time.sleep(2)
        while self.adv_player.is_playing():
            time.sleep(2)

    def get_silent(self):
        for silent in self.current_schedule['silent']:
            time_start = datetime.datetime.combine(datetime.date.today(), silent['time_start'])
            time_end = datetime.datetime.combine(datetime.date.today(), silent['time_end'])
            if time_start<=datetime.datetime.now()<=time_end:
                if self.main_player.is_playing():
                    self.fade_out_main_player()
                    self.main_player.stop()
                self.sleep_flag = True
                self.sleep_time = datetime.datetime.combine(datetime.date.today(), silent['time_end'])
                return True
        return False

    def keep_silent(self):
        if self.sleep_flag:
            if self.sleep_time < datetime.datetime.now():
                self.sleep_flag = False
                self.sleep_time = None
        return self.sleep_flag

    def run_main_player(self):
        state = str(self.main_player.get_state())
        if self.main_player_change or state in ('State.Ended', 'State.Error'):
            if self.main_player.is_playing():
                self.fade_out_main_player()
                self.main_player.stop()
            self.main_player.set_mrl(self.current_schedule['main_stream']['url'])
            self.main_player.audio_set_volume(MAIN_PLAYER_MIN_VOLUME)
            self.main_player_change = False
        if not self.main_player.is_playing():
            self.main_player.play()
            self.fade_in_main_player()

    def run(self):
        while True:
            time.sleep(CYCLE_DELAY_SEC)
            print("run")
            if self.is_change_sch():
                print("is_change_sch()")
                self.save_schedule()
                self.format_raw_schedule()
                self.set_schedule()
            if self.current_schedule is None:
                continue
            if self.keep_silent():
                print("keep_silent()")
                continue
            if self.get_adv_player():
                print("get_adv_player()")
                self.fade_out_main_player()
                self.main_player.pause()
                self.run_adv_player()
                self.run_main_player()
            if self.get_silent():
                print("get_silent()")
                continue
            self.run_main_player()
            print("run_main_player()")
            
player = Player()

if __name__ == '__main__':
    player.run()
