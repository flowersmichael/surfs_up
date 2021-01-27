# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Access the SQLite database
engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect the database into our classes
Base = automap_base()
# Reflect the database, tables
Base.prepare(engine, reflect=True)
# Create variables for each of the classes so we can reference later
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create a session link
session = Session(engine)
# Define our Flask app. This will create a Flask application called "app."
# The __name__ variable in this code is a special type of variable in Python. 
# Its value depends on where and how the code is run.
app = Flask(__name__)
# Welcome route (aka "root" just to be extra confusing)
@app.route("/")
# Create function
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')
#Create the precipitation route
@app.route("/api/v1.0/precipitation")
#Create the precipitation function
def precipitation():
    #Calculate date one year ago from most recent date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Get the precipitation for the previous year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    #Convert dictionary to json file
    return jsonify(precip)

#Create the stations route
@app.route("/api/v1.0/stations")
#Create the stations function
def stations():
    #Create a query that will get all of the stations in our database.
    results = session.query(Station.station).all()
    #Unravel our results into a one-dimensional array
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
    #Convert unraveled results into a list
    stations = list(np.ravel(results))
    #Jsonify the list to return it as JSON
    return jsonify(stations=stations)

#Create the temperature observations route
@app.route("/api/v1.0/tobs")
#Create the temperature observations function
def temp_monthly():
#Calculate the date one year ago from the last date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #Query the primary station for all the temperature observations from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    #Unravel our results into a one-dimensional array
    temps = list(np.ravel(results))
    #Jsonify the list to return it as JSON
    return jsonify(temps=temps)

#Create the statistics route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
#Create the statistics function
def stats(start=None, end=None):
    #Create a list called "sel"
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    #Since we need to determine the starting and ending date, 
    #add an if-not statement to our code.
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        #Unravel our results into a one-dimensional array
        temps = list(np.ravel(results))
        #Jsonify the list to return it as JSON
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
