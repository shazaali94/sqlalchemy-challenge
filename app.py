# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)


# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, autoload_with=engine)
# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Save references to each table
stations = session.query(Station).all()
for station in stations:
    print(station.name) 
# Create our session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


#################################################
# Flask Routes

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Query for the dates and precipitation observations from the last year.
    one_year_ago = datetime.now() - timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Query all stations.
    results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list.
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query the last year of temperature observations for the most active station.
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.id).desc()).first()[0]
    one_year_ago = datetime.now() - timedelta(days=365)
    results = session.query(Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= one_year_ago).all()
    session.close()

    # Convert list of tuples into normal list.
    temperature_observations = list(np.ravel(results))
    return jsonify(temperature_observations=temperature_observations)
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    session = Session(engine)
    # Query TMIN, TAVG, TMAX with start (and optional end date).
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if end:
        results = session.query(*sel).\
                  filter(Measurement.date >= start).\
                  filter(Measurement.date <= end).all()
    else:
        results = session.query(*sel).\
                  filter(Measurement.date >= start).all()
    session.close()

    # Convert list of tuples into normal list.
    temps = list(np.ravel(results))
    return jsonify(temps=temps)