#!/usr/bin/python3

import sys
import getopt
import configparser
from os import path

from IMAPMailLoader import IMAPMailLoader


def print_help(error=''):
    if error != '':
        print(
            '%s is empty but needed. Please use the config.ini file or command line arguments to provide the %s' % (error,error)
        )
    print('usage: load_imap_emails.py -s <server> -u <user> -p <password> -f <path> [-t]')


def create_ini_file():
    cfg = configparser.ConfigParser()
    cfg['IMAP'] = {'server': '', 'username': '', 'password': '', 'tls': 'False'}
    cfg['Paths'] = {'html_path': "", "archive_path": ""}
    cfg['Data'] = {"csv_file_path": ""}
    with open ('config.ini', 'w') as configfile:
        cfg.write(configfile)
    print('Created dummy config file')


if __name__ == '__main__':
    options = "hgts:u:p:f:a:"
    long_options = [
        "tls",
        "server=",
        "username=",
        "password=",
        "path=",
        "archive="
    ]
    try:
        opts, args = getopt.getopt(sys.argv[1:], options, long_options)
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    server = user = password = file_path = archive = ""
    tls = False

    if path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if 'IMAP' in config:
            if 'server' in config['IMAP']:
                server = config['IMAP']['server']
            if 'username' in config['IMAP']:
                user = config['IMAP']['username']
            if 'password' in config['IMAP']:
                password = config['IMAP']['password']
            if 'tls' in config['IMAP']:
                tls = config['IMAP']['tls'] == 'True'
        if 'Paths' in config:
            if 'html_path' in config['Paths']:
                file_path = config['Paths']['html_path']
            if 'archive_path' in config['Paths']:
                archive = config['Paths']['archive_path']

    for opt, val in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        if opt == '-g':
            create_ini_file()
            sys.exit()
        elif opt in ('-s', '--server'):
            server = val
        elif opt in ('-u', '--user'):
            user = val
        elif opt in ('-p', '--password'):
            password = val
        elif opt in ('-f', '--path'):
            file_path = val
        elif opt in ('-a', '--archive'):
            archive = val
        elif opt in ('-t', '--tls'):
            tls = True

    if server == "":
        print_help(error='server')
        sys.exit(2)
    if user == "":
        print_help(error='user')
        sys.exit(2)
    if password == "":
        print_help(error='password')
        sys.exit(2)
    if file_path == "":
        print_help(error='path')
        sys.exit(2)
    if archive == "":
        print_help(error='archive')
        sys.exit(2)

    loader = IMAPMailLoader(server, user, password, file_path, archive, tls)
    loader.load_emails()


