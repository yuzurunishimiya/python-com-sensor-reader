import os
import json
import mysql.connector
import time
import serial

def read_setting():
    with open('setting.json') as f:
        setting = json.load(f)
        f.close()
        return setting

def begin_serial():
    com = setting['com']
    try:
        try:
            ser = serial.Serial(com['com1'], baudrate=9600, timeout=1.0)
        except:
            ser = serial.Serial(com['com2'], baudrate=9600, timeout=1.0)
        return ser
    except Exception as error:
        time.sleep(1)
        # coba save error di database atau log error, atau kirim ke mana aja (telegram, wa, fb)
        # biasanya kalo pakai service systemd atau pm2 bisa ke log
        print("log error: ", error) 
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
        # diganti sesuai dengan yang diperlukan
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
    main()
