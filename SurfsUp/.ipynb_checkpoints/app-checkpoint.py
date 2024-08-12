# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]<br/>"
        f"/api/v1.0/[start]/[end]"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # query & session close
    date = dt.datetime(2016,8,23)
    results = session.query(measurement.station,measurement.date,measurement.prcp).\
        filter(measurement.date > date).\
        order_by(measurement.date).all()

    session.close()

    # dictionary from row data and append process
    precipitation_measure = []
    for station, date, prcp in results:
        prcp_dict = {}
        prcp_dict["station"] = station
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_measure.append(prcp_dict)

    return jsonify(precipitation_measure)

# Stations route
@app.route("/api/v1.0/stations")
def stations():

    # query & session close
    results = session.query(station.station).all()

    session.close()

    # convert to list and jsonify
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():

    # query & session close
    results = session.query(measurement.date,measurement.tobs).\
        filter(measurement.station == 'USC00519281').all()

    session.close()
    
    # dictionary from results and append process
    temperature_data = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temperature_data.append(temp_dict)

    return jsonify(temperature_data)

# start-no-end route
@app.route("/api/v1.0/<start>")
def start(strtdate):

    # query & session close
    results = session.query(func.max(measurement.tobs),func.min(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= strtdate).\
        order_by(measurement.date).all()

    session.close()

    # statistics calculation and jsonify
    stats = []
    stat_dict = {}
    stat_dict["maximum"] = results[0][0]
    stat_dict["minimum"] = results[0][1]
    stat_dict["average"] = results[0][2]
    stats.append(stat_dict)

    return jsonify(stats)

# start-and-end route
@app.route("/api/v1.0/<start>/<end>")
def startend(strtdate,enddate):

    # query & session close
    results = session.query(func.max(measurement.tobs),func.min(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= strtdate).\
        filter(measurement.date <= enddate).\
        order_by(measurement.date).all()

    session.close()

    # statistics calculation and jsonify
    stats = []
    stat_dict = {}
    stat_dict["maximum"] = results[0][0]
    stat_dict["minimum"] = results[0][1]
    stat_dict["average"] = results[0][2]
    stats.append(stat_dict)

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
