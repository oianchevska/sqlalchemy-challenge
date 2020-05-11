from flask import Flask, jsonify
import numpy as np
from sqlalchemy import and_
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = base.classes.measurement
Station = base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (f"Available Routes:<br/> "
            f"/api/v1.0/precipitation<br/> "
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/&ltstart&gt<br/>"
            f"/api/v1.0/&ltstart&gt/&ltend&gt")


# Convert the query results to a dictionary using date as the key and prcp as the value.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    date_prcp = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    result = {}
    for date, prcp in date_prcp:
        result[date] = prcp
    return jsonify(result)


# Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_date = session.query(Station.station).all()
    session.close()
    result = list(np.ravel(station_date))
    return jsonify(result)


# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    station_temp = session.query(Measurement.date, Measurement.tobs).filter(
        and_(Measurement.station == 'USC00519281',
             Measurement.date >= (dt.datetime.strptime(last_day[0], '%Y-%m-%d') - dt.timedelta(days=366)))).all()
    session.close()
    result_temp=[ {"date": rec[0], "tobs": rec[1]} for rec in station_temp]
    return jsonify(result_temp)


# Calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def agg_start(start):
    session = Session(engine)
    temp_range = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),
                               func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()
    result_statrt = list(np.ravel(temp_range))
    return f'Data for all dates greater than and equal to the {start}:<br/> Minimum temperature: {result_statrt[0]}<br/>Maximum temperature: {result_statrt[1]}<br/>Average temperature: {result_statrt[2]}'


@app.route("/api/v1.0/<start>/<end>")
def agg_start_end(start, end):
    session = Session(engine)
    temp_start_end = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs),
                                   func.avg(Measurement.tobs)).filter(
        and_(Measurement.date >= start, Measurement.date <= end)).all()
    session.close()
    result = list(np.ravel(temp_start_end))
    return f'Data for dates between {start} and {end} inclusive:<br/>Minimum temperature: {result[0]}<br/>Maximum temperature: {result[1]}<br/>Average temperature: {result[2]}'


if __name__ == '__main__':
    app.run(debug=True)
