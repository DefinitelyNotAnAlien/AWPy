#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from time import sleep
import requests
try:
    logging.debug('Attempting to import socketIO_client library...')
    from .socketIO_client_next import SocketIO
    SocketIO_Client_Loaded = True
    logging.info('socketIO_client library loaded.')
except ModuleNotFoundError:
    logging.warning('''Failed to import socketIO_client, only the REST API can
                     be accessed.''')
    SocketIO_Client_Loaded = False


ENDPOINT = 'https://api.ambientweather.net'
REST_ENDPOINT = 'https://api.ambientweather.net/v1/devices/?'
HTTPError = {404: 'Not found',
             429: 'Too many requests',
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
        self.callback = {}
        logging.info(('Created AmbientAPI instance with Application key: {} '
                     'and API keys: {}').format(self.Appkey,
                                                self.Apikeys
                                                )
                     )

    def getAllData(self, max_retries=0):
        """Request weather data for all the Apikeys in the class."""
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

                else:
                    ErrorMsg = HTTPError.get(r.status_code, 'Unknown error')
                    if attempts == max_retries:
                        logging.warning(
                                        ('Request returned code {}: {}, '
                                         'maximum number of retries reached, '
                                         'skipping...'
                                         ).format(r.status_code, ErrorMsg)
                                        )
                    else:
                        logging.warning(
                                        ('Request returned code {}: {}, '
                                         ' retrying...'
                                         ).format(r.status_code, ErrorMsg)
                                        )
                        sleep(1)  # Sleep for 1 second to avoid 429 error
                    attempts += 1

            if i+1 != len(self.Apikeys) and (i+1) % 3 == 0:
                # If current apikey isn't the last and 3 requests have been
                # made in a row, sleep before requesting the next one.
                # Application Keys get 3 requests per second, while apikeys
                # only get 1 request per second.
                sleep(1)

    def connect(self, auto_subscribe=False):
        """Connect to the AW Realtime API."""
        if not SocketIO_Client_Loaded:
            logging.critical('No socketIO_client library detected, '
                             'Realtime API cannot be accessed.'
                             )
            raise Exception('No SocketIO Client Library detected.')
        self.auto_subscribe = auto_subscribe
        logging.debug('Connecting to the Ambient Weather Realtime API...')
        self.SocketIO = SocketIO(ENDPOINT, 443, transports=['websocket'],
                                 params={'api': '1',
                                         'applicationKey': self.Appkey})
        self.SocketIO.on('connect', self.connected)
        self.SocketIO.on('data', self.data)
        self.SocketIO.on('subscribed', self.subscribed)
        self.wait = self.SocketIO.wait

    def subscribe(self, apikeys=None):
        """Emit a subscribe command to the Realtime API.

        If no Apikeys are set the function will automatically subscribe to the
        class' Apikeys attribute.
        """
        if not apikeys:
            apikeys = self.Apikeys
        elif type(apikeys) != list:
            apikeys = [apikeys]
        logging.debug('Attempting to subscribe to the following API keys: '
                      ' {}'.format(apikeys)
                      )
        self.SocketIO.emit('subscribe', {"apiKeys": apikeys})

    def on(self, event, callback):
        """Set the callback function for any of the API events.

        Valid events for the API are: "connect", "data" and "subscribed"
        """
        self.callback[event] = callback
        logging.info('Set {} as callback for event {}'.format(callback, event))

    def data(self, weather_data):
        """Call the set function for the 'data' event.

        If no function is set the event data will be printed.
        """
        try:
            self.callback['data'](weather_data)
        except KeyError:
            logging.debug('No callback set for "data" event.')
            print(weather_data)

    def connected(self, *args):
        """Call the set function for the 'connect' event."""
        logging.info('Connected succesfully.')
        try:
            self.callback['connect'](args)
        except KeyError:
            logging.debug('No callback set for "connected" event.')
            # print('Connected to Ambient Weather Realtime API.')
        finally:
            if self.auto_subscribe:
                self.subscribe()

    def subscribed(self, sub_data):
        """Call the set function for the 'subscribed' event.

        If no function is set, a list of the subscribed devices will be
        printed.
        """
        try:
            self.callback['subscribed'](sub_data)
        except KeyError:
            logging.debug('No callback set for "subscribed" event.')
            devices = [dev['info']['name'] for dev in sub_data['devices']]
            print('Subscribed to the following weather stations: '
                  '{}'.format(devices))
