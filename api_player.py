import vlc
import datetime
import time
import requests
import copy
import json
from json.decoder import JSONDecodeError
import sys
import hashlib
import os
import subprocess

# In URL - "localhost:8000" change to your DEPLOY server URL
########
URL = "http://localhost:8000/api/1/"
########

PLAYER_VERSION = 2017120401

###Freq. request to server( in seconds)
REQUEST_PERIOD = datetime.timedelta(seconds=20)

### ADV_DELAY Must be grater when CYCLE_DELAY_SEC
ADV_DELAY = datetime.timedelta(seconds=10)

# Don`t touch it (or touch if you set it)
CYCLE_DELAY_SEC = 5
###
NETWORK_CACHE_MS = 3000
VERBOSE_LEVEL = 2
DEBUG = True
FILE_LAST_SCHEDULE = 'last_schedule.json'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'
MAIN_PLAYER_MIN_VOLUME = 10

STATUS_TYPE = {
        'ОК': 0,
        'Нет текущего расписания': 1,
        'Главный поток закончился': 2,
        'Ошибка главного плеера': 3,
        'Ошибка рекламного плеера': 4
}

CMD = {
    'OK': 0,
    'Schedule': 1,
    'Update': 2
}
UPDATER_FILE = 'updater.py'

# options for get_config and Player identification
CONFIG_FILE = 'config-player.json'

# after class Player __init__, CONFIG_FILE_MAP obtain values for keys that in CONFIG_FILE_REQUIRED_FIELDS(at least)
CONFIG_FILE_MAP = {'player_id': '', 'secret': '', 'url_api_server': ''}



def get_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            settings = json.load(file)
    except FileNotFoundError as error:
        print('Файл настроек \'{}\' не обнаружен в текущей директории!!!'.format(CONFIG_FILE))
        with open(CONFIG_FILE, "w") as file:
            json.dump(CONFIG_FILE_MAP, file, indent=4)
        print('Подготовлен файл настроек \'{}\' в текущей директори.'.format(CONFIG_FILE))
        print('Обязательно заполните поля: \'%s\', открыв указанный файл в любом текстовом редакторе.' %
              ('\', \''.join(CONFIG_FILE_MAP.keys())))
        input('Для завершения нажмите ENTER: ')
        sys.exit(error)

    required_field = []
    for key in CONFIG_FILE_MAP.keys():
        if key in settings and settings.get(key, False):
            CONFIG_FILE_MAP[key] = settings[key]
        else:
            required_field.append(key)
    if required_field:
        print(required_field)
        print('Обязательно заполните поля: \'%s\', открыв файл \'%s\' в любом текстовом редакторе.' %
              ('\', \''.join(required_field), CONFIG_FILE))
        input('Для завершения нажмите ENTER: ')
        sys.exit()


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
        self.time_next_request = None

    def time_to_send(self):
        now_time = datetime.datetime.now()
        if self.time_next_request is None:
            self.time_next_request = now_time
            return True
        if now_time > self.time_next_request:
            self.time_next_request = now_time + REQUEST_PERIOD
            return True
        return False

    def is_change_sch(self):
        if not self.time_to_send():
            return False
        if self.current_schedule is None:
            sch = self.get_local_schedule()
            if sch is not None:
                self.raw_schedule = sch
                self.format_raw_schedule()
                self.set_schedule()
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
        try:
            with open(FILE_LAST_SCHEDULE) as file:
                schedule = json.load(file)
        except (FileExistsError, FileNotFoundError, JSONDecodeError) as error:
            print(error)
            return None
        return schedule

    def save_schedule(self):
        try:
            with open(FILE_LAST_SCHEDULE, "w") as file:
                json.dump(self.raw_schedule, file, indent=4)
        except TypeError as e:
            print(e)

    def set_schedule(self):
        self.main_player_change = True
        self.sleep_flag = False
        self.sleep_time = None
        self.current_schedule = copy.deepcopy(self.raw_schedule)
        self.raw_schedule = None

#status prepare

    def get_info(self):
        form = {'status': self.get_status(), 'timestamp': self.get_timestamp(),
                'current_sch_time': self.get_schedule_time(), 'sig': self.get_sig(),
                'player_version': PLAYER_VERSION, 'updater_present': self.get_updater_file()}
        return form


    def get_status(self):
        #1
        if not self.current_schedule:
            return STATUS_TYPE['Нет текущего расписания']
        #2
        if str(self.main_player.get_state()) == 'State.Ended':
            return STATUS_TYPE['Главный поток закончился']
        #3
        if str(self.main_player.get_state()) == 'State.Error':
            return STATUS_TYPE['Ошибка главного плеера']
        #4
        if str(self.adv_player.get_state()) == 'State.Error':
            # self.adv_player = self.vlc_instance.media_player_new()
            return STATUS_TYPE['Ошибка рекламного плеера']
        #0
        return STATUS_TYPE['ОК']

    def get_id(self):
        return CONFIG_FILE_MAP['player_id']

    def get_timestamp(self):
        return datetime.datetime.now().strftime(DATETIME_FORMAT)

    def get_schedule_time(self):
        return self.current_schedule and self.current_schedule['change_time'].strftime(DATETIME_FORMAT)

    def get_sig(self):
        sig = hashlib.md5()
        sig.update((CONFIG_FILE_MAP['secret']).encode())
        sig.update((self.get_id()).encode())
        return sig.hexdigest()

    def get_updater_file(self):
        return os.path.exists(UPDATER_FILE) and os.path.isfile(UPDATER_FILE)

#end status cooking

    def request_schedule(self):
        url = CONFIG_FILE_MAP['url_api_server']+self.get_id()+'/'
        try:
            answer_raw = requests.post(url, data=self.get_info())
            answer = answer_raw.json()
        except requests.exceptions.ConnectionError as error:
            return None
        # if not answer: return None
        #0 == 'OK'
        if answer['cmd']== CMD['OK']:
            print("GET OK ")
            return None
        #1 == 'Schedule'
        if answer['cmd']== CMD['Schedule']:
            print("GET SCH ")
            self.raw_schedule = answer['Schedule']
            self.save_schedule()
            return None
        #2 == 'Update'
        if answer['cmd']== CMD['Update']:
            print('Update')
            server_response = requests.get(url=answer['Update']['url'])
            with open(answer['Update']['file_type'], 'wb') as updater:
                updater.write(server_response.content)
            self.update()
            return None

    def update(self):
        if self.adv_player is not None: self.adv_player.stop()
        if self.main_player is not None: self.main_player.stop()
        time.sleep(2)
        cmd = 'python updater.py {}'.format(os.getpid()).split()
        if os.path.exists(UPDATER_FILE) and os.path.isfile(UPDATER_FILE):
            print('RUN UPDATER')
            subprocess.Popen(cmd)
            sys.exit(0)


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
                self.format_raw_schedule()
                self.set_schedule()
                # time.sleep(1)
                # self.save_schedule()
            if self.current_schedule is None:
                print('IN NO CURR')
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
            print('api_player PID ', os.getpid())


player = Player()

if __name__ == '__main__':
    get_config()
    player.run()
