import json
import platform
from subprocess import Popen, PIPE
from re import findall
import threading
import time
import ssl
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import configparser
import ipaddress


# a program to monitor my network and send alerts for devices that connect or disconnect________________________________
class NetworkMonitor:
    def __init__(self):
        load_dotenv()

        self.addresses = {}

        # email variables______________________________________________________
        self.sender_email = "example@email.com"
        self.recipient_email = "example@email.com"
        self.email_password = os.getenv("EMAIL_KEY")
        self.smtp_server = "smtp.gmail.com"
        self.port = 465
        self.default_notify = True
        self.new_device_notify = True

        # JSON  variables______________________________________________________
        self.json_filepath = "netmon.json"

        # monitoring variables_________________________________________________
        self.check_delay_seconds = 15
        self.ip_list = ["192.168.1.0/24", "192.168.2.1", "192.168.2.5"]

        self.load_config()
        self.parse_ip_list()
        self.start()

    # load users config from the config file____________________________________________________________________________
    def load_config(self):
        config = configparser.ConfigParser()
        config.read("netmon.cnf")

        # email variables______________________________________________________
        self.sender_email = config.get("email_notifications", "sender_email")
        self.recipient_email = config.get("email_notifications", "recipient_email")
        self.smtp_server = config.get("email_notifications", "smtp_server")
        self.port = int(config.get("email_notifications", "port"))
        self.default_notify = eval(config.get("email_notifications", "default_notify"))
        self.new_device_notify = eval(config.get("email_notifications", "new_device_notify"))

        # JSON  variables______________________________________________________
        self.json_filepath = config.get("json", "json_filepath")

        # Monitoring variables_________________________________________________
        self.check_delay_seconds = int(config.get("monitoring", "check_delay_seconds"))
        self.ip_list = eval(config.get("monitoring", "ip_list"))

    # parse ip list_____________________________________________________________________________________________________
    def parse_ip_list(self):
        new_ip_list = []
        for ip in self.ip_list:
            for address in ipaddress.IPv4Network(ip):
                new_ip_list.append(str(address))
        self.ip_list = new_ip_list

    # pull all known devices from the json file and load into memory____________________________________________________
    def get_addresses(self):
        try:
            with open(self.json_filepath, 'r') as file:
                self.addresses = json.load(file)
        except FileNotFoundError:
            self.set_json()

    # dump the current connection status from memory to the json file___________________________________________________
    def set_json(self):
        with open(self.json_filepath, 'w') as file:
            json.dump(self.addresses, file, indent=4)

    # send a singular ping to the specified address then parse the result and handle properly___________________________
    def send_ping(self, address):
        if platform.system() == "Linux":
            ping_command = ["ping", address, "-c", "1"]
            pattern = 'rtt'
        elif platform.system() == "Windows":
            ping_command = ["ping", address, "-n", "1"]
            pattern = 'TTL'
        else:
            raise ValueError(f"Unsupported platform {platform.system()}")
        data = ""  # used to aggregate responses
        output = Popen(ping_command, stdout=PIPE, encoding="utf-8")  # runs ping command

        # parse ping response
        for line in output.stdout:
            data = data + line
            result = findall(pattern, data)

        # if we get echo reply add device when new, reset notify countdown
        if result:
            try:
                content = self.addresses[address].split()
                # content[0] = notify countdown
                # content[1] = ip address
                # content[2] = name in notification
                # content[3] = notify flag
                self.addresses[address] = f"{4} {content[1]} {content[2]} {content[3]}"

                # If notify flag is set send a reconnected notification
                if content[0] == "-1" and content[3] == "True":
                    subject = "Device Reconnected"
                    message = f"{content[2]} {content[1]} Reconnected"
                    self.send_alert(subject=subject, message=message)

            except KeyError:
                self.addresses[address] = f"4 {address} NewDevice {self.default_notify}"

                # send alert for new device connecting
                if self.new_device_notify:
                    subject = "New Device Connected"
                    message = f"{address} Connected For The First Time"
                    self.send_alert(subject=subject, message=message)

        # if we don't get echo reply and device known drop the notify counter by one
        else:
            try:
                content = self.addresses[address].split()
                if int(content[0]) < 0:
                    content[0] = -1

                # set countdown to negative one and send disconnect alert
                elif int(content[0]) == 0 and content[3] == "True":
                    content[0] = -1
                    subject = "Device Disconnected"
                    message = f"{content[2]} {content[1]} Disconnected"
                    self.send_alert(subject=subject, message=message)

                # drop the countdown by one
                else:
                    content[0] = int(content[0]) - 1

                # content[0] = notify countdown
                # content[1] = ip address
                # content[2] = name in notification
                # content[3] = notify flag
                self.addresses[address] = f"{content[0]} {content[1]} {content[2]} {content[3]}"
            except KeyError:
                pass

    # send an email alert_______________________________________________________________________________________________
    def send_alert(self, subject, message):
        mailer = EmailMessage()
        email = self.recipient_email

        mailer["From"] = self.sender_email
        mailer["To"] = email
        mailer["Subject"] = subject
        mailer.set_content(message)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as smtp:
            smtp.login(self.sender_email, self.email_password)
            smtp.sendmail(self.sender_email, email, mailer.as_string())

    # Start the process loop____________________________________________________________________________________________
    def start(self):
        self.get_addresses()
        while True:
            self.set_json()
            for address in self.ip_list:
                threading.Thread(target=lambda: self.send_ping(address)).start()  # ping on different threads
            time.sleep(self.check_delay_seconds)  # wait before pinging again


NetworkMonitor()
