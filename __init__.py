#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from time import sleep
# from datetime import timedelta, datetime
import requests
try:
    logging.debug('Attempting to import socketIO_client library...')
    from socketIO_client_next import SocketIO
    SocketIO_Client_Loaded = True
    logging.info('socketIO_client library loaded.')
except ModuleNotFoundError:
    logging.warning('''Failed to import socketIO_client, only the REST API can
                     be accessed.''')
    SocketIO_Client_Loaded = False


# logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s')
ENDPOINT = 'https://api.ambientweather.net'
REST_ENDPOINT = 'https://api.ambientweather.net/v1/devices/?'
# ISODate = '%Y-%m-%dT%H:%M:%S.%fZ'
HTTPError = {429: 'Too many requests',
             404: 'Not found',
             502: 'Bad gateway error'
             }


class AW_API(object):
    """Base class for the Ambient Weather API.

    Example usage:
    from AWPy import AW_API
    AW = AW_API(Appkey, [Apikey1, Apikey2, ...])
    """

    def __init__(self, Appkey, Apikeys):
        self.Appkey = Appkey
        self.Apikeys = Apikeys
        logging.info('''Created AmbientAPI instance with Application key: {}
                     and API keys: {}'''.format(self.Appkey,
                                                ", ".join(self.Apikeys)
                                                )
                     )

    def getAllData(self, max_retries=0):
        for i, Apikey in enumerate(self.Apikeys):
            logging.debug('Requesting data for API Key: {}'.format(Apikey))
            attempts = 0
            while attempts <= max_retries:
                r = requests.get(REST_ENDPOINT,
                                 params={'applicationKey': self.Appkey,
                                         'apiKey': Apikey})
                if r:
                    logging.info('Request returned code 200.')
                    yield r.json()
                    break

                elif r.status_code == 401:
                    logging.critical('''One or more of the API keys are
                                      invalid.''')
                    raise Exception

                else:
                    ErrorMsg = HTTPError.get(r.status_code, 'Unknown error')
                    if attempts > max_retries:
                        logging.warning('''Request returned code {}: {},
                                         maximum number of retries reached,
                                         skipping...'''.format(r.status_code,
                                                               ErrorMsg)
                                        )
                    else:
                        logging.warning('''Request returned code {}: {},
                                         retrying...'''.format(r.status_code,
                                                               ErrorMsg)
                                        )
                        sleep(1)
                    attempts += 1

            if not i+1 == len(self.Apikeys):
                # If current apikey isn't the last, sleep before requesting
                # the next one.
                sleep(1)

    def connect(self):
        """Connect to the AW Realtime API."""
        if not SocketIO_Client_Loaded:
            logging.critical('''No socketIO_client library detected, Realtime
                              API cannot be accessed.''')
            raise Exception
        logging.debug('Connecting to the Ambient Weather Realtime API...')
        self.SocketIO = SocketIO(ENDPOINT, 443, transports=['websocket'],
                                 params={'api': '1',
                                         'applicationKey': self.Appkey})

    def subscribe(self, apikeys=None):
        if not apikeys:
            apikeys = self.Apikeys
        self.SocketIO.emit('subscribe', {"apiKeys": apikeys})
        self.SocketIO.wait()

    def on_data(self, callback):
        self.SocketIO.on('data', callback)

    def on_connect(self, callback):
        self.SocketIO.on('connect', callback)

    def on_subscribed(self, callback):
        self.SocketIO.on('subscribed', callback)
