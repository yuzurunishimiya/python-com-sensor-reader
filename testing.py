import os
import json
import mysql.connector
import time
import serial
import random


def read_setting():
    with open('setting.json') as f:
        setting = json.load(f)
        f.close()
        return setting


def begin_serial():
    try:
        try:
            ser = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1.0)
        except:
            ser = serial.Serial('/dev/ttyUSB1', baudrate=9600, timeout=1.0)
        return ser
    except Exception as error:
        print("log error: ", error) # coba save error di database atau log error, atau kirim status ke mana aja (telegram)
        exit()


def connection_msql():
    db = setting['database']
    conn = mysql.connector.connect(
        host=db['host'],
        port=db['port'],
        user=db['user'],
        password=db['password'],
        database=db['database']
    )
    cur = conn.cursor()
    return cur, conn


def insert_to_database(cur, conn, data):
    try:
        cur.execute(f"INSERT INTO {data['source']} (insert_time, \
            temperature, humidity, co, co2) VALUES ({int(time.time())},{data['temp']},{data['hmd']},{data['co']},{data['co2']})")
        conn.commit()
        conn.close()
    except Exception as error:
        return error


def main():
    ser = begin_serial()
    while True:
        sensor_data = ser.readline().decode('utf-8')
        if sensor_data:
            json_data = json.loads(sensor_data)
            cur, conn = connection_msql()
            err = insert_to_database(cur, conn, json_data)
            if err != None:
                print(err) # log error database inserting


if __name__ == "__main__":
    setting = read_setting()
    for i in range(10):
        cur, conn = connection_msql()
        data = {'source': 'Node1', 'temp':random.uniform(1.1, 100.1), 'hmd': random.uniform(1.1, 100.1), 'co': random.uniform(1.1, 100.1), 'co2': random.uniform(1.1, 100.1)}
        err = insert_to_database(cur, conn, data)
        print(err)
        time.sleep(1)