#!/usr/bin/env python3

from sys import argv
from json import loads
from requests import get

def display_ip_location_info(data):
    max_space = max([len(key) for key, _ in data.items()]) + 5
    for key, value in data.items():
        if type(value) != dict:
            print(f"[+]{key}{' ' * (max_space - len(key))}{value}")
        else:
            print(f"[+] {key}")
            max_space_2 = max([len(key) for key, _ in data.items()]) + 5
            for key_2, value_2 in value.items():
                print(f"[*]\t{key_2}{' ' * (max_space_2 - len(key_2))}{value_2}")
    print('\n')

def get_ip_location(ip):
    api_key = "4095b53c881d41babf011f45572dd0b8"
    url = f"https://api.ipgeolocation.io/ipgeo?apiKey={api_key}&ip="
    location_data = []
    data = loads(get(f"{url}{ip}").text)
    location_data.append(data)
    display_ip_location_info(data)
    return location_data

if __name__ == "__main__":
    get_ip_location(argv[1])
