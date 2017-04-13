from flask import Flask
from flask import jsonify
from flask import request
import time
import MySQLdb
import json
import hashlib

DEBUG = True
# DEBUG = False

CONFIG_JSON = "server-config.json"
config = json.load(open(CONFIG_JSON, "r"))

app = Flask(__name__)


@app.route("/")
def hello():
    return "I'm ok"


@app.route("/api", methods=['POST'])
def api():
    resp = {"status": "none"}
    content = request.get_json(silent=True)
    if content:
        if "action" in content:
            if content["action"] == "register":
                if "name" and "key" in content:
                    new_id = register_drone(content["name"])
                    if new_id:
                        hashkey = hashlib.md5(str.encode(str(new_id))).hexdigest()
                        resp = {"status": "registered", "id": new_id, "key": hashkey}
                    else:
                        resp = {"error": "name already registered"}
                else:
                    resp = {"error": "I want more options"}

            if content["action"] == "alive":
                if "id" and "timestamp" in content:
                    drone_event(content["id"], content["timestamp"], 1)
                    if content["id"] == 82:
                        resp = {"status": "get_versions"}
                        return jsonify(resp)
                else:
                    resp = {"error": "I want more options"}

            if content["action"] == "soft_versions":
                if "id" and "software" in content:
                    # for soft_item in content["software"]:
                    resp = {"status": "update", "software": [{"name": content["software"][0]["name"],
                            "version": "2018030301", "url": "http://update.product.in.ua/new/test/test_update.zip"}]}
                else:
                    resp = {"error": "I want more options"}

            if content["action"] == "get_list":
                list = get_list_software()
                resp = {"software": list}

            if content["action"] == "get_schedule":
                if "id" and "state" in content:
                    drone_event(content["id"], "0", 2)
                    orpheus_set_state(content["id"], content["state"])
                resp = {
                        "main_stream": {
                            "url": "http://ic3.101.ru:8000/c2_1",
                            "volume": 100
                        },
                        "inserts": [
                            {
                                "description": "donuts",
                                "time": "18:34:00",
                                "url": "http://hive.product.in.ua/music/reklama_1.mp3",
                                "volume": 80,
                            },
                            {
                                "description": "meat",
                                "time": "20:41:00",
                                "url": "http://hive.product.in.ua/music/reklama_2.mp3",
                                "volume": 80,
                            }
                        ],
                        "silent": [
                            {
                                "description": "lunch break",
                                "time_start": "12:00:00",
                                "time_end": "13:00:00"
                            },
                            {
                                "description": "night1",
                                "time_start": "21:00:00",
                                "time_end": "23:59:59"
                            },
                            {
                                "description": "night2",
                                "time_start": "00:00:00",
                                "time_end": "07:00:00"
                            }
                        ]
                        }
    return jsonify(resp)


@app.route("/api/debug/update",  methods=['GET', 'POST'])
def update():
    resp = {"status": "update", "software": [{"name": "test", "version": "2017010101", "url": "http://update.product.in.ua/new/test/test_update.zip"}]}
    return jsonify(resp)


@app.route("/api/debug/get_ver", methods=['GET', 'POST'])
def get_ver():
    resp = {"status": "get_versions"}
    return jsonify(resp)


def time_stamp():
    return time.time()


def drone_event(drone_id, drone_timestamp, event_id):
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="hive")
    cursor = db.cursor()
    query = ('''INSERT INTO events (drone_id, drone_timestamp, event_id) VALUES ({0},FROM_UNIXTIME({1}),{2}) '''
                    ''' ON DUPLICATE KEY UPDATE drone_timestamp=FROM_UNIXTIME({1}), serverdatetime=CURRENT_TIMESTAMP'''
                   .format(drone_id, drone_timestamp, event_id))
    print(query)
    cursor.execute(query)
    db.commit()
    return 1


def orpheus_set_state(drone_id, state):
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="hive")
    cursor = db.cursor()
    query = ('''INSERT INTO orpheus_states (drone_id, state) VALUES ({0},"{1}")'''
            ''' ON DUPLICATE KEY UPDATE state="{1}"'''.format(drone_id, state))
    print(query)
    cursor.execute(query)
    db.commit()
    return 1


def get_list_software():
    db = MySQLdb.connect(host=config["database"]["host"], user="root", passwd="", db="hive", charset="utf8", use_unicode=True)
    cursor = db.cursor()
    cursor.execute("SELECT name, description, url, version FROM software")
    row_count = cursor.rowcount
    soft = []
    if row_count > 0:
        for (name, description, url, version) in cursor:
            soft_item = {}
            soft_item["name"] = name
            soft_item["description"] = description
            soft_item["version"] = version
            soft_item["url"] = url

            soft.append(soft_item)
    return soft


def get_versions():
    resp = {"status": "get_versions", "timestamp": time_stamp()}
    return jsonify(resp)


def register_drone(drone_name):
    db = MySQLdb.connect(host="localhost", user="root", passwd="", db="hive")
    cursor = db.cursor()
    cursor.execute("SELECT id FROM drones WHERE name='"+drone_name+"'")
    db.commit()
    row_count = cursor.rowcount
    if row_count > 0:
        return 0
    else:
        cursor.execute("INSERT INTO drones (name) VALUES ('"+drone_name+"')")
        db.commit()
        return cursor.lastrowid


if __name__ == "__main__":
    app.run(host=config["server"]["host"], port=config["server"]["port"], debug=DEBUG)

