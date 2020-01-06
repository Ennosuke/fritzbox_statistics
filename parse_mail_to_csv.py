#!/usr/bin/python3

import sys
import getopt
import configparser
from os import path
import os

from HTMLProcessor import HTMLProcessor


def create_ini_file():
    cfg = configparser.ConfigParser()
    cfg['IMAP'] = {'server': '', 'username': '', 'password': '', 'tls': 'False'}
    cfg['Paths'] = {'html_path': "", "archive_path": ""}
    cfg['Data'] = {"csv_file_path": ""}
    with open ('config.ini', 'w') as configfile:
        cfg.write(configfile)
    print('Created dummy config file')


def print_help(error=''):
    if error != '':
        print(
            '%s is empty but needed. Please use the config.ini file or command line arguments to provide the %s' % (error,error)
        )
    print('usage: parse_mail_to_csv.py')


if __name__ == '__main__':
    options = "hga:p:c:"
    long_options = [
        "archive=",
        "path=",
        "data="
    ]
    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    archive = file_path =  csv_path = ""

    if path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'Paths' in config:
            if 'html_path' in config['Paths']:
                file_path = config['Paths']['html_path']
            if 'archive_path' in config['Paths']:
                archive = config['Paths']['archive_path']
        if 'Data' in config:
            if 'csv_file_path' in config['Data']:
                csv_path = config['Data']['csv_file_path']

    for opt, val in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        if opt == '-g':
            create_ini_file()
            sys.exit()
        elif opt in ('-a', '--archive'):
            archive = val
        elif opt in ('-c', '--data'):
            csv_path = val
        elif opt in ('-p', '--path'):
            file_path = val

    if archive == "":
        print_help(error='archive path')
        sys.exit(2)
    if csv_path == "":
        print_help(error='data file path')
        sys.exit(2)
    if file_path == "":
        print_help(error='html file path')
        sys.exit(2)

    processor = HTMLProcessor(archive, csv_path)

    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.html'):
                processor.process(file_path + '\\' + file)
