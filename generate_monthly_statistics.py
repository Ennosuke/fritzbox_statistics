import csv
import matplotlib.pyplot as plt
import numpy as np
import getopt
import sys
from datetime import datetime
from os import path
import configparser


threshold = 10240


def convert_mm_to_hhmm(mm):
    hours = int(mm / 60)
    minutes = int(mm % 60)
    return f'{hours:02}:{minutes:02}'


def convert_hhmm_to_mm(hhmm):
    parts = hhmm.split(':')
    hours_min = int(parts[0])*60
    minutes = int(parts[1])
    return hours_min + minutes


def format_float(value):
    return f'{value:.2f}'


def format_float_with_unit(value_with_unit):
    return format_float(value_with_unit[0]) + ' ' + value_with_unit[1]


def get_right_unit_data(value):
    units = ['MB', 'GB', 'TB']
    times = 0
    new_value = value
    for i in range(len(units)):
        if new_value >= threshold:
            new_value = value / 1024
            times = i+1
            continue
        break
    return [new_value, units[times]]


def generate_statistics(month_for_stats):
    output_path = csv_path = ""
    if path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'Paths' in config:
            if 'output_path' in config['Paths']:
                output_path = config['Paths']['output_path']
        if 'Data' in config:
            if 'csv_file_path' in config['Data']:
                csv_path = config['Data']['csv_file_path']
    if output_path == "" or csv_path == "":
        print('No output or csv path')
        exit(2)
    send = []
    recv = []
    days = []
    total = []
    upload = []
    download = []
    connections = []
    time_online = []
    err_days = 0
    file_name_days_offline = 'img/%s-days-offline.svg' % month_for_stats
    file_name_recv_send = 'img/%s-recv-send.svg' % month_for_stats
    file_name_dev_data = 'img/%s-dev-data.svg' % month_for_stats
    file_name_dev_speed = 'img/%s-dev-speed.svg' % month_for_stats
    file_name_html = '%s/%s.html' % (output_path, month_for_stats)

    with open(csv_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['date'].startswith(month_for_stats):
                send.append(float(row['send']))
                recv.append(float(row['recv']))
                days.append(row['date'].replace(month_for_stats + '-', ''))
                total.append(float(row['total']))
                upload.append(float(row['send_speed']))
                download.append(float(row['recv_speed']))
                connections.append(int(row['connections']))
                online_time = convert_hhmm_to_mm(row['time'])
                time_online.append(online_time)
                if online_time <= 1435:
                    err_days += 1

    if len(days) < 1:
        print('No data for given month')
        exit(2)

    average_download = np.mean(download)
    average_upload = np.mean(upload)
    average_online = np.mean(time_online)

    highest_send = get_right_unit_data(np.max(send))
    highest_send_date = days[send.index(np.max(send))]
    highest_recv = get_right_unit_data(np.max(recv))
    highest_recv_date = days[recv.index(np.max(recv))]
    highest_total = get_right_unit_data(np.max(total))
    highest_total_date = days[total.index(np.max(total))]
    highest_download = np.max(download)
    highest_download_date = days[download.index(highest_download)]
    highest_upload = np.max(upload)
    highest_upload_date = days[upload.index(highest_upload)]
    lowest_download = np.min(download)
    lowest_download_date = days[download.index(lowest_download)]
    lowest_upload = np.min(upload)
    lowest_upload_date = days[upload.index(lowest_upload)]

    total_send = get_right_unit_data(np.sum(send))
    total_recv = get_right_unit_data(np.sum(recv))
    total_data = get_right_unit_data(np.sum(total))
    total_online = np.sum(time_online)

    labels = ['Error Days', 'Good Days']
    pie_data = [err_days, len(days)-err_days]
    pie_colors = ['r', 'g']

    if err_days == 0:
        pie_data.pop(0)
        pie_colors.pop(0)
        labels = ['Good Days']

    fig1, ax1 = plt.subplots()

    ax1.pie(pie_data, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, colors=pie_colors)

    ax1.axis('equal')
    plt.savefig(output_path+'/'+file_name_days_offline)
    plt.close(fig1)

    labels = ['Data send', 'Data received']
    pie_data = [total_send[0], total_recv[0]]
    pie_colors = ['darkorange', 'dodgerblue']

    fig2, ax2 = plt.subplots()

    wedges, texts, autotexts = ax2.pie(pie_data, autopct='%1.1f%%', shadow=False, startangle=90, colors=pie_colors, explode=(0.2, 0), pctdistance=1.1)
    ax2.legend(wedges, labels, title="Direction", loc="center left", bbox_to_anchor=(0.905, 0, 0.5, 1))
    plt.setp(autotexts, weight="bold")
    plt.savefig(output_path+'/'+file_name_recv_send)
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(10, 4.8))
    ax3.plot(days, total, label="Total")
    ax3.legend()
    plt.xlabel('Day of month')
    plt.ylabel('Data (MB)')

    plt.savefig(output_path+'/'+file_name_dev_data)
    plt.close(fig3)

    fig4, ax4 = plt.subplots(figsize=(10, 4.8))
    ax4.plot(days, upload, label="Upload")
    ax4.plot(days, download, label="Download")
    ax4.legend()
    plt.xlabel('Day of month')
    plt.ylabel('Speed in kbit/s')
    plt.savefig(output_path+'/'+file_name_dev_speed)
    plt.close(fig4)

    with open('templates/month.template.html') as template_file:
        template_data = template_file.read()

    template_data = template_data.replace('%month%', month_for_stats)
    template_data = template_data.replace('%image_days_offline_5min%', file_name_days_offline)
    template_data = template_data.replace('%image_data_overall%', file_name_recv_send)
    template_data = template_data.replace('%image_dev_usage%', file_name_dev_data)
    template_data = template_data.replace('%image_dev_speed%', file_name_dev_speed)
    template_data = template_data.replace('%total_time_online%', convert_mm_to_hhmm(total_online))
    template_data = template_data.replace('%average_time_online%', convert_mm_to_hhmm(average_online))
    template_data = template_data.replace('%days_offline_5min%', str(err_days))
    template_data = template_data.replace('%total_data%', format_float_with_unit(total_data))
    template_data = template_data.replace('%received_data%', format_float_with_unit(total_recv))
    template_data = template_data.replace('%send_data%', format_float_with_unit(total_send))
    template_data = template_data.replace('%total_highest%', format_float_with_unit(highest_total))
    template_data = template_data.replace('%send_highest%', format_float_with_unit(highest_send))
    template_data = template_data.replace('%received_highest%', format_float_with_unit(highest_recv))
    template_data = template_data.replace('%average_speed_up%', format_float(average_upload))
    template_data = template_data.replace('%average_speed_down%', format_float(average_download))
    template_data = template_data.replace('%highest_speed_up%', format_float(highest_upload))
    template_data = template_data.replace('%highest_speed_down%', format_float(highest_download))
    template_data = template_data.replace('%lowest_speed_up%', format_float(lowest_upload))
    template_data = template_data.replace('%lowest_speed_down%', format_float(lowest_download))
    template_data = template_data.replace('%send_highest_date%', month_for_stats + '-' + highest_send_date)
    template_data = template_data.replace('%total_highest_date%', month_for_stats + '-' + highest_total_date)
    template_data = template_data.replace('%received_highest_date%', month_for_stats + '-' + highest_recv_date)
    template_data = template_data.replace('%highest_up_date%', month_for_stats + '-' + highest_upload_date)
    template_data = template_data.replace('%highest_down_date%', month_for_stats + '-' + highest_download_date)
    template_data = template_data.replace('%lowest_up_date%', month_for_stats + '-' + lowest_upload_date)
    template_data = template_data.replace('%lowest_down_date%', month_for_stats + '-' + lowest_download_date)

    with open(file_name_html, 'w') as html_file:
        html_file.write(template_data)


def print_usage():
    print(f'usage: {sys.argv[0]}')


if __name__ == "__main__":
    options = 'hm:'
    long_options = ['month=']
    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)

    month = ""

    for opt, val in opts:
        if opt in ['-m', '--month']:
            month = val
        elif opt in ['-h']:
            print_usage()

    if month == "":
        now = datetime.now()
        month = now.strftime('%Y-%m')

    generate_statistics(month)
