# import necessary libraries
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

# Database setup
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# create session link
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Homepage - list all available api routes
@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Query the last 12 months of precipitation data
    max_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.datetime.strptime(max_date, '%Y-%m-%d') - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()

    # Create a dictionary from the row data and append to a list of precipitation_data
    precipitation_data = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

# stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

# tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Query the last 12 months of temperature observation data for the most active station
    max_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.datetime.strptime(max_date, '%Y-%m-%d') - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station)\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).first()[0]
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station)\
        .filter(Measurement.date >= last_year)\
        .all()

    # Create a dictionary from the row data and append to a list of temperature_data
    temperature_data = []
    for date, tobs in results:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs

#/api/v1.0/<start> and /api/v1.0/<start>/<end>

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date"""

    # Query for the temperature stats
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start).all()

    # Create a dictionary from the row data and append to a list of all_temps
    all_temps = []
    for Tmin, Tavg, Tmax in results:
        temp_dict = {}
        temp_dict["TMIN"] = Tmin
        temp_dict["TAVG"] = Tavg
        temp_dict["TMAX"] = Tmax
        all_temps.append(temp_dict)

    # Return the JSON representation of the dictionary
    return jsonify(all_temps)


@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range"""

    # Query for the temperature stats
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                        .filter(Measurement.date >= start)\
                        .filter(Measurement.date <= end).all()

    # Create a dictionary from the row data and append to a list of all_temps
    all_temps = []
    for Tmin, Tavg, Tmax in results:
        temp_dict = {}
        temp_dict["TMIN"] = Tmin
        temp_dict["TAVG"] = Tavg
        temp_dict["TMAX"] = Tmax
        all_temps.append(temp_dict)

    # Return the JSON representation of the dictionary
    return jsonify(all_temps)

if __name__ == "__main__":
    app.run(debug=True)