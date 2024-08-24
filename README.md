# Network Monitor (NetMon)
NetMon is a basic network monitor made in python. It will send you email notifications if 
new or designated devices connect / disconnect from your network. This program is primarily 
built for Linux but will run on Windows as well.

- [Installation](#installation)
  - [Linux](#linux)
  - [Windows](#windows)
- [Configuration](#configuration)
  - [email notifications](#email-notifications)
  - [JSON](#json)
  - [Monitoring](#monitoring)


## Installation
This section will go over how to properly install NetMon. This will go over the installation 
for both Windows and Linux.

### Linux

- Download netmon.tar.gz
- extract the file ``tar -xzf netmon.tar.gz``
- run the setup script as root ``sudo ./netmon/netmon_setup.sh``
- Verify the netmon service is set up ``sudo systemctl status netmon`` the output should look similar to the following
  ```○ netmon.service
       Loaded: loaded (/etc/systemd/system/netmon.service; enabled; preset: enabled)
       Active: inactive (dead) since Sat 2024-08-24 08:12:30 BST; 1min 2s ago
     Duration: 2h 11min 8.551s
      Process: 1547045 ExecStart=python3 /opt/netmon/main.py (code=killed, signal=TERM)
     Main PID: 1547045 (code=killed, signal=TERM)
          CPU: 32min 20.161s
  ```
- Proceed to the [Configuration](#configuration) section

### Windows

- windows install stuffs

## Configuration

General configuration is set in ``/opt/netmon/netmon.cnf``
```
[email_notifications]
sender_email        = email@example.com
recipient_email     = email@example.com
smtp_server         = smtp.gmail.com
port                = 465
default_notify      = True
new_device_notify   = True

[json]
json_filepath       = netmon.json

[monitoring]
check_delay_seconds = 15
ip_list             = ["192.168.1.0/24", "192.168.2.1", "192.168.2.5"]
```

### email notifications

```
sender_email        = email@example.com
recipient_email     = email@example.com
smtp_server         = smtp.gmail.com
port                = 465
default_notify      = True
new_device_notify   = True
```

- sender_email
  - Set this to the email address the notifications will come from
- recipient_email
  - Set this to the email address you would like the notifications to be sent to
- smtp_server
  - The smtp server used, you can probably just leave it
- port
  - The port used to send emails from, probably leave it
- default_notify
  - When this is set to True any new devices will have notification on by default.
    this means you will get notifications whenever the device connects or disconnects
    from the network. Set this to False if you would like to have connect/disconnect
    notifications turned off by default.
- new_device_notify
  - When this is True you will get a notification everytime a new device connects
    to the specified network. Setting this to False means you will no longer
    receive notifications whenever a new device connects.

### JSON

``json_filepath = netmon.json``

All connections are stored and tracked using the specified JSON file. by default 
the JSON file is stored in netmon.json in the same directory as the main.py or main.exe
file.

The JSON wil look similar to the following.
```
{
    "192.168.1.1": "4 192.168.1.1 NewDevice True",
    "192.168.1.7": "4 192.168.1.7 NewDevice True",
    "192.168.1.20": "4 192.168.1.20 NewDevice True"
}
```
You can change the ``NewDevice`` to any name. This name will show in the email
notifications. Name must NOT include spaces.

The parameter set to ``True`` at the end is weather or not notifications are on
for that device. Set it to False in order to disable notifications.

### Monitoring
```
check_delay_seconds = 15
ip_list             = ["192.168.1.0/24", "192.168.2.1", "192.168.2.5"]
```

- check_delay_seconds
  - How often in seconds it will check if devices are connected
- ip_list
  - The ips to be checked for connectivity, You can enter subnets or individual ips