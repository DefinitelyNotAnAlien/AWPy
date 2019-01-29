# AWPy

AWPy is a Python library used to connect to Ambient Weather's API, including support for both the REST API and the Realtime API based in SocketIO.

## Prerequisites

A SocketIO client library that supports SocketIO 2.x and pure websocket connection is required to connect to AW's Realtime API, you can use [this library](https://github.com/DefinitelyNotAnAlien/socketIO-client-2.0.3), if you wish to use a different one change the import statement in line 9.

## Usage

//TODO

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
