# AWPy

AWPy is a Python library used to connect to Ambient Weather's API, including support for both the REST API and the Realtime API based in SocketIO.

## Prerequisites

A SocketIO client library that supports SocketIO 2.x and pure websocket connection is required to connect to AW's Realtime API, you can use [this library](https://github.com/DefinitelyNotAnAlien/socketIO-client-2.0.3), if you wish to use a different one change the import statement in line 9.

## Usage

* Download or clone the repository
* Add the AWPy folder to your PATH, Python's site packages or project folder
* Import the module and create an instance
```
  from AWPy import AW_API

  appkey = 'your AW Application key'
  apikeys = ['station 1 apikey here', 'station 2 apikey here', ...]
  Ambient = AW_API(appkey, apikey)
```

* To use the REST API you can currently use the "getAllData" method, which will return the information for all the weather stations as an iterable. A method that allows you to get data for an specific station (Including rate limiting and end date) will be added later
```
  for station in Ambient.getAllData():
    print(station)
```

* To connect to AW's Realtime API, you can call the "connect" method, this will use the SocketIO client library and your application key to connect. Afterwards subscribe to your desired stations with the "subscribe" method, which will subscribe to all the station API keys by default.
* You can also define callback functions for when you connect to the API ('connect' event), subscribe to a station(s) ('subscribed' event), or receive data from a station ('data' event).
```
  def on_data(weather_data):
    print(f'Temperature is {weather_data["lastData"]["tempf"]}')

  Ambient.on('data', on_data)
  Ambient.connect(auto_subscribe=True)
```

## To-do list

* Add unit conversion to SI units.
* Add documentation and docstrings.
* Add support for timezones (Use strptime and timedelta, perhaps?)
* ~Improve callback functions for Realtime API.~
* Allow checking data for single weather stations in the REST API.

## License

Project licensed under the MIT License

## Credits

* [owise1](https://github.com/owise1) made the original AW API library, which aided me in the making of this library.
* [invisibleroads](https://github.com/InvisibleRoads) made the original socketIO_client library for Python.
* [nexus-devs](https://github.com/nexus-devs) for making the socketIO_client library compatible with SocketIO 2.x
