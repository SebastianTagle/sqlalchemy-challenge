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

engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base= automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/date/<start><br/>"
        f"/api/v1.0/range_date/<start_date>/<end_date><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitaion():
    #here i calculate the date of one year ago    
    one_year=dt.date(2017,8,23)-dt.timedelta(days=365)

    """Return a list with the precipitations by date of the last year"""
    # Query all stations
    results=session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date >= one_year).all()
    
    session.close()
    
    # Create a dictionary from the row data and append to a list with the precipitations of every day 
    prcp_info = []
    for date,prcp in results:
        info = {}
        info["Date"] = date
        info["Precipitation"] = prcp
        prcp_info.append(info)

    return jsonify(prcp_info)

@app.route("/api/v1.0/stations")
def stations():
    
    """Return a list of all stations"""
    # Query all stations
    results=session.query(Station.name).all()
    
    session.close()

    # Convert the results in a list
    station = list(np.ravel(results))
    
    return jsonify(station=station)

@app.route("/api/v1.0/tobs")
def temperatures():
    
    #here i calculate the date of one year ago   
    one_year=dt.date(2017,8,23)-dt.timedelta(days=365)

    """Return a list with the temperature per day of the last year to the station with more activity """
    # Query to get the temperature of most active station in the last year
    results=session.query(Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= one_year).all()    
    
    session.close()
    #convert the result in a list
    temps = list(np.ravel(results))
    
    return jsonify(temps=temps)

@app.route("/api/v1.0/date/<start_date>")
def info_temperatures(start_date=None):
    
    # here, i am changing the format of the date    
    start_date=dt.datetime.strptime(start_date,"%m%d%Y")

    """Return a list with de Max, Min and Average Temperatures"""
    # Query to find the Max, Min and Average Temperatures
    results=session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()    
    
    session.close()
    #temps_start = list(np.ravel(results))

    temperature_info= []
    # Convert list into normal list
    for max,min,avg in results:
        info = {}
        info["Max Temperature"] = max
        info["Min Temperature"] = min
        info["Average Temperature"] = avg
        temperature_info.append(info)

    #return jsonify(temps_start) 
    return jsonify(temperature_info)


@app.route("/api/v1.0/range_date/<start_date>/<end_date>")
def info_temperatures_2(start_date=None,end_date=None):
    
    # here, i am changing the format of the date
    start_date=dt.datetime.strptime(start_date,"%m%d%Y")
    end_date=dt.datetime.strptime(end_date,"%m%d%Y")

    """Return a list with de Max, Min and Average Temperatures"""
    # Query all stations
    results=session.query(func.max(Measurement.tobs),func.min(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date <= end_date).\
        filter(Measurement.date >= start_date).all()    
    
    session.close()

    temperature_info_2= []

    # Convert list into normal list
    for max,min,avg in results:
        info = {}
        info["Max Temperature"] = max
        info["Min Temperature"] = min
        info["Average Temperature"] = avg
        temperature_info_2.append(info)

    return jsonify(temperature_info_2)

if __name__ == '__main__':
    app.run(debug=True)