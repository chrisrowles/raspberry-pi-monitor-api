import os
import subprocess
import psutil
import time

def get_network_info():
    info = {}
    info["ssid"] = get_ssid()
    info["interfaces"] = get_interface_stats()
    info["connections"] = get_connections()

    return info

def get_ssid():
    ssid = subprocess.check_output('iwgetid -r', shell=True).decode().rstrip()

    return ssid

def get_interface_stats():
    interfaces = {}
    for inet,stat in psutil.net_io_counters(pernic=True).items():
        interfaces[inet] = {
            'mb_sent': stat.bytes_sent / (1024.0 * 1024.0),
            'mb_received': stat.bytes_recv / (1024.0 * 1024.0),
            'pk_sent': stat.packets_sent,
            'pk_received': stat.packets_recv,
            'error_in': stat.errin,
            'error_out': stat.errout,
            'dropout': stat.dropout,
        }
    
    return interfaces

def get_connections():
    connections = {}

    for sconn in psutil.net_connections(kind='inet'):
        if sconn.laddr.port == 22 and sconn.status == 'ESTABLISHED':
            connections["ssh"] = {
                "local_port": sconn.laddr.port,
                "remote_ip": sconn.raddr.ip,
            }
    
    return connections

count = 0
qry = ''
def counter(interface):
    ul=0.00
    dl=0.00
    t0 = time.time()
    upload = psutil.net_io_counters(pernic=True)[interface].bytes_sent
    download = psutil.net_io_counters(pernic=True)[interface].bytes_recv
    up_down = (upload,download)
    while True:
        last_up_down = up_down
        upload = psutil.net_io_counters(pernic=True)[interface].bytes_sent
        download = psutil.net_io_counters(pernic=True)[interface].bytes_recv
        t1 = time.time()
        up_down = (upload,download)
        try:
            ul, dl = [(now - last) / (t1 - t0) / 1024.0
            for now,last in zip(up_down, last_up_down)]
            t0 = time.time()
        except:
            pass
        if dl > 0.1 or ul >= 0.1:
            time.sleep(0.75)
            os.system('clear')
            yield 'UL: {:0.2f} kB/s \n'.format(ul) + 'DL: {:0.2f} kB/s '.format(dl)