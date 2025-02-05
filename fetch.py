#!/usr/local/bin/python

#!/usr/bin/env python

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, TIMESTAMP, select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import URL
from geoalchemy2 import Geometry

import os
import requests
import json
import datetime
from dateutil import parser as datetime_parser

class Resource:
	url: str

	def __init__(self, url):
		self.url = url
	
	def fetch(self, params=None):
		res = requests.get(self.url, params)
		try:
			return res.json()
		except Exception:
			return res.text

	def get(self, params=None):
		return requests.get(self.url, params)

class Bikes:
	url: str
	bikes: list

	def __init__(self, url=False, bbox=False):
		self.bbox = bbox
		self.url = url if url is not False else 'https://api.opensensemap.org/boxes'

	def fetch(self):
		params = {"grouptag": "bike"}
		if self.bbox is not False:
			params["bbox"] = f"{self.bbox['W']},{self.bbox['S']},{self.bbox['E']},{self.bbox['N']}"
		res = requests.get(self.url, params)
		
		try:
			response = res.json()
		except Exception:
			print(Exception)
			return

		#create all child objects
		self.bikes = []
		for b in response:
			# get all the sensors of each bike
			sensors = []
			bike = Bike(b["_id"], b["updatedAt"], b["currentLocation"]["coordinates"], sensors=b["sensors"])
			self.bikes.append(bike)

		#return list of all bikes with sensors
		return self.bikes
	
	def getBikes(self):
		return self.bikes
		
class Bike:
	id: str
	sensors: list
	lastUpdate: str
	position: list

	def __init__(self, bike_id, lastUpdate, position, sensors=None):
		self.id = bike_id 
		self.position = position
		self.lastUpdate = lastUpdate
		
		self.sensors = []
		for sensor in sensors:
			new_sensor = Sensor(sensor["_id"], self.id, sensor["unit"], sensor["title"], self.position)
			self.sensors.append(new_sensor)
		return
	
	def __str__(self):
		sensors = []
		for sensor in self.sensors:
			sensors.append(str(sensor))
		return f"{{\"id\": \"{self.id}\", \"updatedAt\": \"{self.lastUpdate}\", \"currentLocation\": {self.position}, \"sensors\": {sensors}}}"
	
	def get_sensors(self, sensor_types=False):
		types = []
		if sensor_types is not False:
			#TODO implement filtering for sensor types
			types = sensor_types
		return self.sensors

	def get_measurements(self, sensor_types=False):
		types = []
		if sensor_types is not False:
			#TODO implement filtering for sensor types
			types = sensor_types
		time_series = []
		for sensor in self.sensors:
			for measurement in sensor.get_measurements():
				time_series.append(measurement)
		return(time_series)

class Sensor:
	id: str
	bike_id: str
	unit: str
	title: str
	position: list

	def __init__(self, sensor_id, bike_id, unit, title, position):
		self.id = sensor_id
		self.bike_id = bike_id
		self.unit = unit
		self.title = title
		self.position = position
		return

	def __str__(self):
		return f"{{\"id\": \"{self.id}\"}}"

	def get_measurements(self, params=False):
		parameters = {}
		if params is not False:
			parameters = params
		else:
			parameters = {"from-date": "1970-01-01T00:00:00.000Z"}
		url = f"https://api.opensensemap.org/boxes/{self.bike_id}/data/{self.id}"

		res = requests.get(url, params=parameters)
		try:
			results = res.json()
		except Exception:
			print("get_measurements for sensor unsuccessful")
			print(Exception)
			return
		
		measurements = []
		for m in results:
			measurement = Measurement(self.id, self.bike_id, self.title, m["value"], self.unit, m["createdAt"], m["location"])
			measurements.append(measurement)
		return measurements

class Measurement:
	sensor_id: str
	bike_id: str
	title: str
	value: str
	unit: str
	time: str
	position: list

	def __init__(self, sensor_id, bike_id, title, value, unit, time, position):
		self.sensor_id = sensor_id
		self.bike_id = bike_id
		self.title = title
		self.value = value
		self.unit = unit
		self.time = time
		self.position = position

class DB_Table:
	drivername: str
	host: str
	port: str|int
	database: str
	username: str
	password: str

	url: URL
	table: Table

	def __init__( self,
			table,
			drivername="postgresql",
			username="gdb",
			host="localhost",
			port="5432",
			database="gdb_db",
			password="gdb",
		):
		self.table = table

		self.drivername = drivername
		self.username = username
		self.password = password
		self.host = host
		self.port = port
		self.database = database

		self.url = URL.create(
			drivername = self.drivername, 
			username = self.username, 
			password = self.password,
			host = self.host, 
			port = self.port, 
			database = self.database, 
		)
		self.engine = create_engine(self.url)

	#insert one or several dicts
	def insert_dict(self, dict):
		connection = self.engine.connect()
		dicts = dict if type(dict) is list else [dict]

		stmt = insert(self.table).values(dicts)
		stmt = stmt.on_conflict_do_nothing()
		res = connection.execute(
			stmt
		)
		connection.commit()
		return res
	
	def insertMeasurements(self, measurement):
		measurements = []
		if type(measurement) is list:
			for m in measurement:
				if type(m) is Measurement:
					measurements.append(m)
		elif type(measurement) is Measurement:
			measurements.append(measurement)

		for m in measurements:
			point = f"srid=4326;POINT({m.position[0]} {m.position[1]})"

			data = {
				"sensor_id": m.sensor_id,
				"bike_id": m.bike_id,
				"measurement_type": m.title,
				"measurement_value":m.value,
				"measurement_unit": m.unit,
				"measurement_time": m.time, #TODO correct formatting
				"position": point #TODO correct formatting
			}
			self.insert_dict(data)

	def latest_measurement_time(self, sensor_id=None):
		connection = self.engine.connect()
		#check for latest measurements in the database
		#SELECT measurement_time from osem_bike_measurements
		#GROUP BY measurement_time
		#ORDER BY max(measurement_time);
		where = ""
		if sensor_id is not None:
			where = f"WHERE sensor_id = '{sensor_id}'"
		expression = f"SELECT measurement_time FROM osem_bike_measurements {where} GROUP BY measurement_time ORDER BY max(measurement_time) LIMIT 1;"
		res = connection.execute(text(expression))
		connection.commit()

		rows = res.all()
		if len(rows) == 0:
			return "1970-01-01T00:00:00.000Z"
		
		for row in res:
			if rows == None:
				return "1970-01-01T00:00:00.000Z"
			print(row[0])
			return row[0]
		return


	def insertBikes(self, bike):
		bikes = []
		if type(bike) is list:
			for b in bike:
				if type(b) is Bike:
					bikes.append(b)
		elif type(bike) is Bike:
			bikes.append(bike)
		
		res = None
		for b in bikes:
			point = f"srid=4326;POINT({b.position[0]} {b.position[1]})"
			data = {
				"bike_id": b.id,
				"last_update": b.lastUpdate,
				"position": point
			}
			res = self.insert_dict(data)
		return res

class Bike_writer_agent:
	def __init__(self, bike_table, measurement_table):
		self.bike_table = bike_table
		self.measurement_table = measurement_table
		return

	def fetch_latest_measurements(self, city, max_lookback=None):
		bbox = None
		if city == "os":
			bbox = {
				"W": "7.85", "S": "52.19", "E": "8.17", "N": "52.37"
			}
		elif city == "ms":
			bbox={
				"W": "7.50", "S": "51.87", "E": "7.75", "N": "52.02"
			}
		
		#get all the bikes with their sensors
		bikes = Bikes(bbox=bbox)
		bikes.fetch()
		bikes_list = bikes.getBikes()
		self.bike_table.insertBikes(bikes_list)

		for bike in bikes_list:
			#for each sensor on each bike:
			sensors = bike.get_sensors()
			if len(sensors) == 0:
				continue
			print(len(sensors))
			
			#get the date of latest measurements
			latest_timestamp = self.measurement_table.latest_measurement_time(sensors[0].id)
			if (latest_timestamp == "1970-01-01T00:00:00.000Z" or latest_timestamp == None) and max_lookback is not None:
				#use a timestamp 2 weeks ago
				current = datetime.datetime.utcnow() #.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
				d = datetime.timedelta(days = max_lookback)
				previous = current-d
				latest_timestamp = previous.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

			#check first, if current bike even has updates since then
			print(sensors[0].id)
			print(bike.lastUpdate)
			print(latest_timestamp)

			if datetime_parser.parse(latest_timestamp) > datetime_parser.parse(bike.lastUpdate):
				continue

			for sensor in sensors:
				#fetch new measurements that have been made since
				measurements = sensor.get_measurements({"from-date": latest_timestamp})
				#write new measurements to table
				self.measurement_table.insertMeasurements(measurements)


if __name__ == '__main__':
	metadata = MetaData()
	bike_table = DB_Table(
		Table(
			"osem_bikes",
			metadata,
			Column("internal_id", Integer, primary_key=True),
			Column("bike_id", String),
			Column("last_update", TIMESTAMP),
			Column("position")
		)
	)
	measurement_table = DB_Table(
		Table(
			"osem_bike_measurements",
			metadata,
			Column("internal_id", Integer, primary_key=True),
			Column("sensor_id", String),
			Column("bike_id", String, unique=True),
			Column("measurement_type", String),
			Column("measurement_value", String),
			Column("measurement_unit", String),
			Column("measurement_time", TIMESTAMP),
			Column("position", Geometry(geometry_type='POINT', srid=4326)),
		)
	)
	agent = Bike_writer_agent(bike_table, measurement_table)
	agent.fetch_latest_measurements("ms", 35)