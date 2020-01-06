import csv
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from os import path
import os


def find_data_table(tag):
    return tag.get_text().strip() == 'Zeitraum'


def find_speed_information(tag):
    return tag.get_text().strip() == 'Aktuelle Datenrate:'


def get_text_striped(tag):
    return tag.get_text().strip()


class HTMLProcessor:

    def __init__(self, archive_path, csv_file):
        self._archive_path = archive_path
        self._csv_file = csv_file
        self._multipliers = {'MB': 1, 'GB': 1024, 'TB': 1024*1024}

    def normalize_size(self, string):
        parts = string.split(' ')
        num = float(parts[0])
        weight = parts[1]
        if weight not in self._multipliers:
            print('Unknown unit returning string')
            return string
        return num * self._multipliers[weight]

    def process(self, file):
        print('Processing file ', file)
        with open(file, "r") as input_file:
            input_data = input_file.read()
        file_name = path.basename(file)
        if path.exists(self._archive_path):
            os.rename(file, self._archive_path+path.sep+file_name)
        date_string = file_name.split(sep='.')[0]
        date_object = datetime.strptime(date_string, '%Y-%m-%d')
        yesterday = date_object - timedelta(days=1)
        parsed_data = BeautifulSoup(input_data, 'html.parser')

        online_time = ""
        volume_total = ""
        volume_recv = ""
        volume_send = ""
        connections = ""
        zeitraum_tag = parsed_data.find(find_data_table)
        if zeitraum_tag is None:
            print('Zeitraum Tag not found')
            return
        if zeitraum_tag.parent is None:
            print('Parent of Zeitraum not found')
            return
        if zeitraum_tag.parent.parent is None:
            print ('Table of Zeitraum not found')
            return
        online_counter_table = zeitraum_tag.parent.parent

        for row in online_counter_table.find_all('tr'):
            if row.th is not None:
                continue
            cells = row.find_all('td')
            if get_text_striped(cells[0]) != 'Gestern':
                continue

            online_time = get_text_striped(cells[1])
            volume_total = self.normalize_size(get_text_striped(cells[2]))
            volume_send = self.normalize_size(get_text_striped(cells[3]))
            volume_recv = self.normalize_size(get_text_striped(cells[4]))
            connections = get_text_striped(cells[5])

        speed_info_tag = parsed_data.find(find_speed_information)

        if speed_info_tag is None:
            print('No speed data found')
            return
        recv_speed_tag = speed_info_tag.find_next_sibling(name='td')
        if recv_speed_tag is None:
            print('No receive speed data found')
            return
        recv_speed = get_text_striped(recv_speed_tag).split(' ')[0]

        send_speed_tag = recv_speed_tag.find_next_sibling(name='td')
        if send_speed_tag is None:
            print('No send speed data found')
            return
        send_speed = get_text_striped(send_speed_tag).split(' ')[0]

        header = True
        if path.exists(self._csv_file):
            header = False
        with open(self._csv_file, "a", newline='') as f:
            data_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if header:
                data_writer.writerow(['date', 'time', 'total', 'send', 'recv', 'connections', 'recv_speed', 'send_speed'])

            data_writer.writerow([yesterday.strftime('%Y-%m-%d'), online_time, volume_total, volume_send, volume_recv, connections, recv_speed, send_speed])