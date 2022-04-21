#!/usr/bin/env python3

import http.server
import traceback
import sys
import time
import json
import urllib.request
import os
import logging
import datetime
import opsgenie_sdk
import prometheus_client
import prometheus_client.core
import pprint


def get_config():
    '''Get configuration from ENV variables'''
   #conf['opsgenie_api_key'] = ''
   #conf['opsgenie_query'] = ''
    conf['log_level'] = 'INFO'
    env_text_options = ['opsgenie_api_key', 'opsgenie_query', 'log_level']
    for opt in env_text_options:
        opt_val = os.environ.get(opt.upper())
        if opt_val:
            conf[opt] = opt_val
    conf['opsgenie_pagination_limit'] = 100
    conf['opsgenie_days_limit'] = 30
    conf['main_loop_sleep_interval'] = 10
    conf['listen_port'] = 9647
    env_int_options = ['opsgenie_pagination_limit', 'opsgenie_days_limit', 'main_loop_sleep_interval', 'listen_port']
    for opt in env_int_options:
        opt_val = os.environ.get(opt.upper())
        if opt_val:
            conf[opt] = int(opt_val)

def configure_logging():
    '''Configure logging module'''
    log = logging.getLogger(__name__)
    log.setLevel(conf['log_level'])
    FORMAT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT)
    return log

class Opsgenie:
    '''Object to work with opsgenie'''
    def __init__(self, opsgenie_api_key):
        self.conf = self.conf = opsgenie_sdk.configuration.Configuration()
        self.conf.api_key['Authorization'] = opsgenie_api_key
        self.api_client = opsgenie_sdk.api_client.ApiClient(configuration=self.conf)
        self.alert_api = opsgenie_sdk.AlertApi(api_client=self.api_client)
        self.alerts = list()

    def get_alerts(self):
        '''Get alerts with filter'''
        query = conf['opsgenie_query']
        offset = 0
        while True:
            alerts = self.alert_api.list_alerts(offset=offset, limit=conf['opsgenie_pagination_limit'], query=query).to_dict()['data']
            date_limit = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=conf['opsgenie_days_limit'])
            for alert in alerts:
                if alert['created_at'].replace(tzinfo=datetime.timezone.utc) > date_limit:
                    self.alerts.append(alert)
                else:
                    return
            offset += conf['opsgenie_pagination_limit']

    def get_alerts_counters(self):
        '''Get alerts counters'''
        self.count_stats = count_stats = dict()
        for alert in opsgenie.alerts:
            message = alert['message']
            close_time = alert['report']['close_time']
           #print(close_time, message)
            if message not in count_stats:
                count_stats[message] = {
                    'count': 1,
                    'close_time': close_time
                }
            else:
                count_stats[message]['count'] += 1
                count_stats[message]['close_time'] += close_time
        print('||counter||avg close time (m)||message||comment||')
        for message in count_stats:
            counter = count_stats[message]['count']
            avg_close_time = (count_stats[message]['close_time'] / count_stats[message]['count']) / 1000 / 60
            message_formated = message.replace('|', '\|')
            print('|{}|{}|{}|-|'.format(counter, avg_close_time, message_formated))
       #pprint.pprint(opsgenie.alerts)

if __name__ != 'main':
    conf = dict()
    get_config()
    log = configure_logging()
    log.debug('Config: "{}"'.format(conf))
    opsgenie = Opsgenie(conf['opsgenie_api_key'])
    opsgenie.get_alerts()
    opsgenie.get_alerts_counters()
