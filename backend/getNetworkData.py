import datetime
import os
import time

import pandas
import psutil
import subprocess
import json
import ipaddress
import socket

from scapy.all import *
from scapy.layers.dot11 import Dot11Beacon, Dot11, Dot11Elt
from scapy.layers.l2 import ARP, Ether

def parse_nmap_output(nmap_output):
    result = []
    current_host = None

    # Regular expressions for parsing host information
    host_regex = re.compile(r'Nmap scan report for\s+(.*?)\s*\((.*?)\)')
    mac_address_regex = re.compile(r'MAC Address:\s+([0-9A-Fa-f:]+)\s+\((.*?)\)')

    nmap_output_str = nmap_output.decode('utf-8')

    # Split the Nmap output by lines and iterate over each line
    for line in nmap_output_str.splitlines():
        # Match host information
        host_match = host_regex.match(line)
        if host_match:
            if current_host:
                result.append(current_host)
            current_host = {
                'host': host_match.group(1),
                'ip': host_match.group(2),
                'mac_address': None,
                'latency': None
            }
        else:
            continue

        # Match MAC Address and latency information
        mac_address_match = mac_address_regex.search(line)
        if mac_address_match:
            current_host['mac_address'] = mac_address_match.group(1)
            current_host['vendor'] = mac_address_match.group(2)

        # Match latency information
        latency_match = re.search(r'(\d+(\.\d+)?)(s latency)?', line)
        if latency_match:
            current_host['latency'] = float(latency_match.group(1))

    # Append the last host to the result list
    if current_host:
        result.append(current_host)

    return result

def parse_additional_details(additional_details):
    pass
def get_local_network_info():
    network_info = {}

    # Get network interfaces information using psutil
    network_info['interfaces'] = {}
    for interface, addrs in psutil.net_if_addrs().items():
        interface_info = []
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interface_info.append({
                    'ipv4_address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast_address': addr.broadcast
                })
        network_info['interfaces'][interface] = interface_info

    # Execute system command to get more network details
    process = subprocess.Popen(['ipconfig', '/all'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #process = subprocess.Popen(['ip', 'address'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = process.communicate()
    if error:
        print("Error occurred while executing command:", error.decode())
    else:
        network_info['additional_details'] = output.decode()

    # Extract DNS server information from the output
    dns_servers = []
    lines = output.decode().split('\n')
    for line in lines:
        if 'DNS Servers' in line:
            print(1, line)
            dns_servers.extend(line.split(':')[1].strip().split(', '))
            print(2, line.split(':')[1].strip().split(', '))
    network_info['dns_servers'] = dns_servers

    return network_info

def nmap_network(wifi_address, collect_24=False):
    range_subnet = ""
    #if collect_24:

    range_subnet = "/28"
    nmap_cmd = ['nmap', '-sn', wifi_address+f"{range_subnet}"]
    print("NMAP Command: ", nmap_cmd)
    process = subprocess.Popen(nmap_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    print(parse_nmap_output(output))
    print(error)
    parsed_wifi_connectors = parse_nmap_output(output)

    return parsed_wifi_connectors

def export_to_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def get_network_information(default_interface="Wi-Fi"):
    local_network_info = get_local_network_info()

    # change if needed
    default_interface = "Ethernet 2"
    wifi_ipv4_address = local_network_info["interfaces"][default_interface][0]["ipv4_address"]
    # wifi_ipv4_address - replace if needed
    dns_address = local_network_info['dns_servers'][0]
    wifi_ipv4_address_subnet_24 = nmap_network(wifi_address=dns_address)

    # Combine local network interface information and network scan results

    print("test1", local_network_info['additional_details'])
    local_network_info['additional_details'] = "" # remove unnecessary data
    print("test2", local_network_info['additional_details'])
    find_host = lambda data, ip: [entry['host'] for entry in data if entry['ip'] == ip]

    network_info = {
        'dns_servers': local_network_info['dns_servers'],
        'local_network_info': local_network_info,
        'wifi_ipv4_addresses': {
            f'my_ip': {'host': 'pc1', 'ip': wifi_ipv4_address,
                       'dns_host_name': find_host(wifi_ipv4_address_subnet_24, local_network_info["dns_servers"][0])[0]},
            f'{local_network_info["dns_servers"][0]}/28': wifi_ipv4_address_subnet_24
        },
        'timestamp': str(datetime.now())
    }

    return network_info

def clean_output(output):
    # Remove leading and trailing whitespace
    cleaned_output = output.strip()

    # Remove extra spaces
    cleaned_output = re.sub(r'\s+', ' ', cleaned_output)

    # Remove carriage return and newline characters
    cleaned_output = cleaned_output.replace('\r', '').replace('\n', '')

    return cleaned_output

def json_to_lab_confu(json_data):
    # DNS scenario
    lab_confu = ""

    # Extract my_ip from JSON data
    my_ip = json_data["my_ip"]

    # Write pc1 line
    hostname = my_ip["host"]
    ip_address = my_ip["ip"]
    dns_host_name = my_ip["dns_host_name"]

    lab_confu += f"{hostname}[0]=\"A\"        $ip({ip_address}/16); has_name({hostname}.{dns_host_name})\n"
    lab_confu += f"$ns_resolv({hostname}, {dns_host_name.replace('.', '_').replace('-', '')}|eth0)\n\n"

    # Set resources specifically for u of m
    u_of_m_dns = [
        {
            "host": "umanitoba.ca",
            "ip": "130.179.16.50",
            "mac_address": "null",
            "latency": "null"
        },
        {
            "host": "cc.umanitoba.ca",
            "ip": "130.179.1.1",
            "mac_address": "null",
            "latency": "null"
        }
    ]

    data = json_data
    data['u_of_m_dns_extra'] = u_of_m_dns

    for key, val in data.items():
        if key != 'my_ip':
            for item in json_data[key]:
                hostname_loc = item["host"].replace(".", "_").replace("-", "")
                ip_address_loc = item["ip"]
                lab_confu += f"{hostname_loc}[0]=\"A\"     $ip({ip_address_loc}/16)\n"

    lab_confu += "\n\n"

    for key, val in data.items():
        if key != 'my_ip':
            for item in json_data[key]:
                hostname_loc = item["host"].replace(".", "_").replace("-", "")
                ip_address_loc = item["ip"]

                lab_confu += f"$dns({hostname_loc}, eth0, {item['host']}, master)\n"

    return lab_confu

if __name__ == "__main__":
    res = get_network_information()
    print("------------------")
    print(res)
    data = res["wifi_ipv4_addresses"]
    export_to_json(data, f"data_{datetime.now().strftime('%Y-%m-%dT%H-%M-%S')}.json")

    print(data)
    lab_confu_content = json_to_lab_confu(data)

    # Save lab.confu content to a file named lab.confu
    with open("lab.confu", "w") as file:
        file.write(lab_confu_content)

