# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#1 - homepage and availible routes
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"Precipitation Data for the Last 12 Months:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"A List of Weather Stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"The Dates and Temperature Observations of the Most-Active Station for the Previous Year:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Minimum, Average, and Maximum Temperature for a specified Start Date (Format:yyyy-mm-dd):<br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"Minimum, Average, and Maximum Temperatures for a specified Start Date and End Date (Format:yyyy-mm-dd/yyyy-mm-dd):<br/>"
        f"/api/v1.0/<start>/<end>"
    )

#2 - precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # create session 
    session = Session(engine)
    
    # calculate the date one year from the last date in data set
    year_prior = dt.date(2017,8,23) - dt.timedelta(days = 365)
    
    # retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_prior).all()
    
    # close the session                                                 
    session.close()
    
    # create an empty dictionary to store data and iterate through 
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_data.append(prcp_dict)
    #Return the JSON representation of the dictionary.   
    return jsonify(prcp_data)

#3 - stations
@app.route("/api/v1.0/stations")
def stations():
    
    # create session
    session = Session(engine)
    
    # retrieve data for all stations
    stations = session.query(Base.classes.station.name, 
                             Base.classes.station.station, 
                             Base.classes.station.elevation, 
                             Base.classes.station.latitude, 
                             Base.classes.station.longitude).all()
    
    
    # close Session                                                  
    session.close()
    
    # create dictionary 
    station_data = []
    for name, station, elevation, latitude, longitude in stations:
        station_dict = {}
        station_dict["Name"] = name
        station_dict["Station ID"] = station
        station_dict["Elevation"] = elevation
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_data.append(station_dict)
    #Return a JSON list of stations from the dataset.    
    return jsonify(station_data)

#4 - temperature observations
@app.route("/api/v1.0/tobs")
def tobs():
    
    # create a session
    session = Session(engine)
    
    # calculate the date one year from the last date in data set
    year_prior = dt.date(2017,8,23) - dt.timedelta(days = 365)
    
    # retrieve the dates and temperature observations of the most-active station for the previous year of data
    active_station = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').\
                              filter(measurement.date >= year_prior).all()
    
    # close the session                                                  
    session.close()
    
    # create dictionary
    most_active = []
    for date, temp in active_station:
        active_dict = {}
        active_dict[date] = temp
        most_active.append(active_dict)
    #Return a JSON list of temperature observations for the previous year.   
    return jsonify(most_active)

#5a - Minimum, Average, and Maximum Temperature for a specified Start Date
@app.route("/api/v1.0/<start>")
def start(start):

    # create session 
    session = Session(engine)
    
    # retrieve the minimum, maximum, and average temperature for a specified start date of the dataset
    query_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).all()
    
    # close session                                                  
    session.close()
    
    # create dictionary
    start_date = []
    for min, max, avg in query_results:
        start_dict = {}
        start_dict["Minimum Temperature"] = min
        start_dict["Maxium Temperature"] = max
        start_dict["Average Temperature"] = avg
        start_date.append(start_dict)
    # Return JSON list of the Minimum, Average, and Maximum Temperature for a specified Start Date.
    return jsonify(start_date)

#5b - Minimum, Average, and Maximum Temperatures for a specified Start Date and End Date
@app.route("/api/v1.0/<start>/<end>")
def range_date(start,end):
    
    # create session
    session = Session(engine)
    
    # retrieve the minimum, maximum, and average temperature for a specified start date to the end of the dataset
    query_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # close session                                                  
    session.close()
    
    # create dictionary 
    range_date = []
    for min, max, avg in query_results:
        range_dict = {}
        range_dict["Minimum Temperature"] = min
        range_dict["Maxium Temperature"] = max
        range_dict["Average Temperature"] = avg
        range_date.append(range_dict)
    # Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.    
    return jsonify(range_date)
    
if __name__ == '__main__':
    app.run(debug=True)