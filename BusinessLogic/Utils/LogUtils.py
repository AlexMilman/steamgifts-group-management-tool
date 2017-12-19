import ConfigParser
import logging

# Utilities for working with logs
# Copyright (C) 2017  Alex Milman

config = ConfigParser.ConfigParser()
config.read('application.config')
dir = config.get('Logging', 'Directory')
file_name = config.get('Logging', 'FileName')

logging.basicConfig(format='%(asctime)s %(message)s', filename=dir + file_name, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())


def log_debug(message):
    logging.debug(message)

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)
